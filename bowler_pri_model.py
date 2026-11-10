import os
import pandas as pd
import numpy as np
from scipy.stats import zscore

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

# Match metadata
matches_info = matches[['match_id', 'comp_id', 'stage', 'knock_out', 'win_team_id', 'result', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']]
matches_info = matches_info.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

df = df.merge(matches_info, on='match_id', how='left')
df['is_legal_ball'] = ~df['extras_type'].isin(['wide', 'Overstep'])

def get_ball_team_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 1 if ext_type in ['wide', 'legbyes', 'byes', 'Overstep', 'other'] else 0
    return r + extras + ext2

df['ball_team_runs'] = df.apply(get_ball_team_runs, axis=1)

def get_bowler_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 1 if ext_type in ['wide', 'Overstep', 'other'] else 0
    return r + extras + ext2

df['bowler_runs'] = df.apply(get_bowler_runs, axis=1)
df['is_bowler_wicket'] = df['is_wicket'] & ~df['dismissal_type'].isin(['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field'])

df['cum_team_runs'] = df.groupby(['match_id', 'innings'])['ball_team_runs'].cumsum()
df['cum_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
df['legal_balls_bowled'] = df.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum()

# 1st innings total
inn1_totals = df[df['innings'] == 1].groupby('match_id')['cum_team_runs'].max().reset_index()
inn1_totals.rename(columns={'cum_team_runs': 'inn1_final_runs'}, inplace=True)
df = df.merge(inn1_totals, on='match_id', how='left')

df['target'] = np.where(df['revised_target'].notna(), df['revised_target'], df['inn1_final_runs'] + 1)
df['runs_needed'] = df['target'] - df['cum_team_runs'] + df['ball_team_runs']
df['max_legal_balls'] = np.where(
    (df['innings'] == 1) & df['first_inn_revised_overs'].notna(), df['first_inn_revised_overs'] * 6,
    np.where((df['innings'] == 2) & df['second_inn_revised_overs'].notna(), df['second_inn_revised_overs'] * 6, 120)
)
df['balls_remaining'] = np.maximum(0, df['max_legal_balls'] - df['legal_balls_bowled'] + df['is_legal_ball'].astype(int))
df['wickets_in_hand'] = 10 - (df['cum_wickets'] - df['is_wicket'].astype(int))
df['rrr'] = np.where(df['balls_remaining'] > 0, df['runs_needed'] / (df['balls_remaining'] / 6.0), np.nan)

# Pressure conditions
p_inn2_death = (df['innings'] == 2) & (df['overid'] >= 15) & (df['runs_needed'] > 0) & (df['rrr'] >= 6.0) & (df['rrr'] <= 24.0) & (df['wickets_in_hand'] >= 1)
p_inn2_rrr = (df['innings'] == 2) & (df['overid'] >= 10) & (df['rrr'] >= 10.0) & (df['balls_remaining'] <= 66) & (df['wickets_in_hand'] >= 2) & (df['runs_needed'] > 0)
p_inn2_crisis = (df['innings'] == 2) & (df['overid'] <= 7) & (df['cum_wickets'] >= 3) & (df['rrr'] >= 8.5)

p_inn1_death = (df['innings'] == 1) & (df['overid'] >= 16)
p_inn1_crisis = (df['innings'] == 1) & (
    ((df['cum_wickets'] >= 3) & (df['overid'] <= 7) & (df['cum_team_runs'] <= 50)) |
    ((df['cum_wickets'] >= 4) & (df['overid'] <= 11) & (df['cum_team_runs'] <= 75))
)
p_super_over = df['innings'].isin([3, 4])

df['is_pressure'] = p_inn2_death | p_inn2_rrr | p_inn2_crisis | p_inn1_death | p_inn1_crisis | p_super_over
df['ball_weight'] = np.where(df['knock_out'] == 1, 1.25, 1.0)

# Bowler overall
overall_bowl = df.groupby(['bowler_id', 'bowler_name']).agg(
    balls_all=('is_legal_ball', 'sum'),
    deliveries_all=('bowler_runs', 'count'),
    runs_all=('bowler_runs', 'sum'),
    wickets_all=('is_bowler_wicket', 'sum')
).reset_index()
overall_bowl['econ_all'] = (overall_bowl['runs_all'] / overall_bowl['balls_all']) * 6.0
overall_bowl['sr_all'] = np.where(overall_bowl['wickets_all'] > 0, overall_bowl['balls_all'] / overall_bowl['wickets_all'], 50)

# Bowler match-level consistency in pressure situations
# For each bowler in each match where they bowled under pressure:
bowl_match = df[df['is_pressure']].groupby(['match_id', 'bowler_id', 'bowler_name']).agg(
    p_balls=('is_legal_ball', 'sum'),
    p_runs=('bowler_runs', 'sum'),
    p_wickets=('is_bowler_wicket', 'sum')
).reset_index()
bowl_match = bowl_match[bowl_match['p_balls'] >= 6].copy() # At least 1 full over under pressure
bowl_match['p_econ'] = (bowl_match['p_runs'] / bowl_match['p_balls']) * 6.0
# Impact spell under pressure: p_econ <= 8.5 (under league avg of 9.19) OR p_wickets >= 2
bowl_match['is_impact_spell'] = (bowl_match['p_econ'] <= 8.5) | (bowl_match['p_wickets'] >= 2)

bowl_consistency = bowl_match.groupby(['bowler_id', 'bowler_name']).agg(
    total_press_spells=('match_id', 'count'),
    impact_spells=('is_impact_spell', 'sum'),
    econ_std=('p_econ', 'std')
).reset_index()
bowl_consistency['impact_rate'] = bowl_consistency['impact_spells'] / bowl_consistency['total_press_spells']

# Bowler pressure aggregates
press_bowl = df[df['is_pressure']].groupby(['bowler_id', 'bowler_name']).agg(
    balls_press=('is_legal_ball', 'sum'),
    deliveries_press=('bowler_runs', 'count'),
    runs_press=('bowler_runs', 'sum'),
    wickets_press=('is_bowler_wicket', 'sum'),
    dots_press=('bowler_runs', lambda x: (x == 0).sum()),
    fours_press=('is_four', 'sum'),
    sixes_press=('is_six', 'sum'),
    matches_press=('match_id', 'nunique'),
    ko_balls_press=('knock_out', 'sum')
).reset_index()
press_bowl['boundaries_press'] = press_bowl['fours_press'] + press_bowl['sixes_press']

bowl = press_bowl.merge(overall_bowl, on=['bowler_id', 'bowler_name']).merge(bowl_consistency, on=['bowler_id', 'bowler_name'])

# Filter minimum sample size: >= 200 pressure balls (or >= 150)
bowl = bowl[bowl['balls_press'] >= 150].copy()

# Rates
bowl['econ_press'] = (bowl['runs_press'] / bowl['balls_press']) * 6.0
bowl['sr_press'] = np.where(bowl['wickets_press'] > 0, bowl['balls_press'] / bowl['wickets_press'], 50.0)
bowl['avg_press'] = np.where(bowl['wickets_press'] > 0, bowl['runs_press'] / bowl['wickets_press'], 100.0)
bowl['dot_pct_press'] = (bowl['dots_press'] / bowl['deliveries_press']) * 100
bowl['boundary_pct_press'] = (bowl['boundaries_press'] / bowl['deliveries_press']) * 100

# Non-pressure baseline
bowl['balls_nonpress'] = bowl['balls_all'] - bowl['balls_press']
bowl['runs_nonpress'] = bowl['runs_all'] - bowl['runs_press']
bowl['wickets_nonpress'] = bowl['wickets_all'] - bowl['wickets_press']
bowl['econ_baseline'] = np.where(bowl['balls_nonpress'] >= 50, (bowl['runs_nonpress'] / bowl['balls_nonpress']) * 6.0, bowl['econ_all'])
# Regress baseline toward league mean (8.41)
bowl['econ_base_reg'] = (bowl['balls_nonpress'] * bowl['econ_baseline'] + 100 * 8.41) / (bowl['balls_nonpress'] + 100)

# Delta economy: how much better/worse does bowler perform compared to baseline and league pressure par (9.19)
bowl['delta_econ'] = bowl['econ_base_reg'] - bowl['econ_press'] # higher is better (positive means suppresses runs)

# PRI Bowler model
# Z-scores (invert economy, bowling strike rate, boundary pct so higher z-score is better)
bowl['z_econ'] = -zscore(bowl['econ_press'])
bowl['z_sr'] = -zscore(bowl['sr_press'])
bowl['z_dots'] = zscore(bowl['dot_pct_press'])
bowl['z_boundary_prev'] = -zscore(bowl['boundary_pct_press'])
bowl['z_impact'] = zscore(bowl['impact_rate'])
bowl['z_vol'] = zscore(np.log(bowl['balls_press']))
bowl['z_wickets'] = zscore(np.log(bowl['wickets_press'].clip(lower=1)))

# Composite PRI Bowler score:
# Weights:
# Economy & Run Suppression: 30% (z_econ 20%, z_boundary 10%)
# Breakthrough & Wickets: 25% (z_sr 15%, z_wickets 10%)
# Dot Ball Pressure: 15% (z_dots)
# Consistency across spells: 15% (z_impact)
# Volume & Captain Trust: 15% (z_vol)
bowl['pri_bowl'] = (
    0.20 * bowl['z_econ'] +
    0.10 * bowl['z_boundary_prev'] +
    0.15 * bowl['z_sr'] +
    0.10 * bowl['z_wickets'] +
    0.15 * bowl['z_dots'] +
    0.15 * bowl['z_impact'] +
    0.15 * bowl['z_vol']
)

bowl['pri_bowl_score'] = 50 + (bowl['pri_bowl'] / bowl['pri_bowl'].std()) * 15

print("=== TOP 25 BOWLERS UNDER PRESSURE (PRI SCORE) ===")
top_bowl = bowl.sort_values('pri_bowl_score', ascending=False).reset_index(drop=True)
top_bowl['rank'] = top_bowl.index + 1
print(top_bowl[['rank', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'impact_rate', 'pri_bowl_score']].head(25).to_string())


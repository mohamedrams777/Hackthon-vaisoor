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

# Pressure definitions
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

# League pressure constants
LEAGUE_SR_PRESS = 139.65
LEAGUE_ECON_PRESS = 9.19
LEAGUE_BSR_PRESS = 13.05
LEAGUE_AVG_PRESS = 25.0

# ----------------- BATTER BAYESIAN MODEL -----------------
overall_bat = df.groupby(['striker_id', 'striker_name']).agg(
    balls_all=('runs', 'count'),
    runs_all=('runs', 'sum'),
    dismissals_all=('is_wicket', 'sum')
).reset_index()

press_bat = df[df['is_pressure']].groupby(['striker_id', 'striker_name']).agg(
    balls_press=('runs', 'count'),
    runs_press=('runs', 'sum'),
    dismissals_press=('is_wicket', 'sum'),
    fours_press=('is_four', 'sum'),
    sixes_press=('is_six', 'sum'),
    dots_press=('runs', lambda x: (x == 0).sum()),
    matches_press=('match_id', 'nunique'),
    ko_balls_press=('knock_out', 'sum')
).reset_index()

# Batter match consistency
batter_match = df[df['is_pressure']].groupby(['match_id', 'striker_id', 'striker_name']).agg(
    p_runs=('runs', 'sum'),
    p_balls=('runs', 'count'),
    p_dismissed=('is_wicket', 'sum')
).reset_index()
batter_match['p_sr'] = (batter_match['p_runs'] / batter_match['p_balls']) * 100
batter_match['is_impact_inning'] = ((batter_match['p_runs'] >= 20) & (batter_match['p_sr'] >= 135)) | (batter_match['p_runs'] >= 35)

bat_consistency = batter_match.groupby(['striker_id', 'striker_name']).agg(
    total_press_innings=('match_id', 'count'),
    impact_innings=('is_impact_inning', 'sum')
).reset_index()
bat_consistency['impact_rate'] = bat_consistency['impact_innings'] / bat_consistency['total_press_innings']

bat = press_bat.merge(overall_bat, on=['striker_id', 'striker_name']).merge(bat_consistency, on=['striker_id', 'striker_name'])

# Filter minimum sample size: >= 200 pressure balls faced
bat = bat[bat['balls_press'] >= 200].copy()

# Bayesian shrunk strike rate and average under pressure (prior weight M = 120 balls)
M_bat = 120
bat['sr_press_shrunk'] = (bat['runs_press'] + (M_bat * LEAGUE_SR_PRESS / 100.0)) / (bat['balls_press'] + M_bat) * 100.0
bat['avg_press_shrunk'] = (bat['runs_press'] + (10 * LEAGUE_AVG_PRESS)) / (bat['dismissals_press'] + 10)

# Non-pressure baseline regressed
bat['balls_nonpress'] = bat['balls_all'] - bat['balls_press']
bat['runs_nonpress'] = bat['runs_all'] - bat['runs_press']
bat['sr_base_reg'] = (bat['runs_nonpress'] + (100 * 131.4 / 100.0)) / (bat['balls_nonpress'] + 100) * 100.0
bat['delta_sr_shrunk'] = bat['sr_press_shrunk'] - bat['sr_base_reg']

bat['boundary_pct_press'] = ((bat['fours_press'] + bat['sixes_press']) / bat['balls_press']) * 100
bat['dot_pct_press'] = (bat['dots_press'] / bat['balls_press']) * 100
bat['sr_press_raw'] = (bat['runs_press'] / bat['balls_press']) * 100
bat['avg_press_raw'] = bat['runs_press'] / bat['dismissals_press'].replace(0, 0.5)

# Z-scores
bat['z_sr'] = zscore(bat['sr_press_shrunk'])
bat['z_avg'] = zscore(np.log(bat['avg_press_shrunk']))
bat['z_delta_sr'] = zscore(bat['delta_sr_shrunk'])
bat['z_boundary'] = zscore(bat['boundary_pct_press'])
bat['z_impact'] = zscore(bat['impact_rate'])
bat['z_vol'] = zscore(np.log(bat['balls_press']))

# Batter PRI Score
bat['pri_bat'] = (
    0.25 * bat['z_sr'] +
    0.20 * bat['z_avg'] +
    0.20 * bat['z_delta_sr'] +
    0.20 * bat['z_impact'] +
    0.15 * bat['z_vol']
)
bat['pri_bat_score'] = 50 + (bat['pri_bat'] / bat['pri_bat'].std()) * 15
top_batters = bat.sort_values('pri_bat_score', ascending=False).reset_index(drop=True)
top_batters['rank'] = top_batters.index + 1

print("=== REFINED TOP 15 BATTERS UNDER PRESSURE ===")
print(top_batters[['rank', 'striker_name', 'balls_press', 'runs_press', 'sr_press_raw', 'avg_press_raw', 'delta_sr_shrunk', 'boundary_pct_press', 'impact_rate', 'pri_bat_score']].head(15).to_string())

# ----------------- BOWLER BAYESIAN MODEL -----------------
overall_bowl = df.groupby(['bowler_id', 'bowler_name']).agg(
    balls_all=('is_legal_ball', 'sum'),
    runs_all=('bowler_runs', 'sum'),
    wickets_all=('is_bowler_wicket', 'sum')
).reset_index()

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

# Bowler match consistency
bowl_match = df[df['is_pressure']].groupby(['match_id', 'bowler_id', 'bowler_name']).agg(
    p_balls=('is_legal_ball', 'sum'),
    p_runs=('bowler_runs', 'sum'),
    p_wickets=('is_bowler_wicket', 'sum')
).reset_index()
bowl_match = bowl_match[bowl_match['p_balls'] >= 6].copy()
bowl_match['p_econ'] = (bowl_match['p_runs'] / bowl_match['p_balls']) * 6.0
bowl_match['is_impact_spell'] = (bowl_match['p_econ'] <= 8.5) | (bowl_match['p_wickets'] >= 2)

bowl_consistency = bowl_match.groupby(['bowler_id', 'bowler_name']).agg(
    total_press_spells=('match_id', 'count'),
    impact_spells=('is_impact_spell', 'sum')
).reset_index()
bowl_consistency['impact_rate'] = bowl_consistency['impact_spells'] / bowl_consistency['total_press_spells']

bowl = press_bowl.merge(overall_bowl, on=['bowler_id', 'bowler_name']).merge(bowl_consistency, on=['bowler_id', 'bowler_name'])

# Filter minimum sample size: >= 200 pressure balls bowled
bowl = bowl[bowl['balls_press'] >= 200].copy()

# Bayesian shrunk economy and strike rate under pressure (prior weight M = 120 balls)
M_bowl = 120
bowl['econ_press_shrunk'] = ((bowl['runs_press'] + (M_bowl * LEAGUE_ECON_PRESS / 6.0)) / (bowl['balls_press'] + M_bowl)) * 6.0
bowl['sr_press_shrunk'] = (bowl['balls_press'] + M_bowl) / (bowl['wickets_press'] + (M_bowl / LEAGUE_BSR_PRESS))

bowl['econ_press_raw'] = (bowl['runs_press'] / bowl['balls_press']) * 6.0
bowl['sr_press_raw'] = bowl['balls_press'] / bowl['wickets_press'].replace(0, 0.5)
bowl['dot_pct_press'] = (bowl['dots_press'] / bowl['deliveries_press']) * 100
bowl['boundary_pct_press'] = (bowl['boundaries_press'] / bowl['deliveries_press']) * 100

# Z-scores
bowl['z_econ'] = -zscore(bowl['econ_press_shrunk'])
bowl['z_sr'] = -zscore(bowl['sr_press_shrunk'])
bowl['z_dots'] = zscore(bowl['dot_pct_press'])
bowl['z_boundary_prev'] = -zscore(bowl['boundary_pct_press'])
bowl['z_impact'] = zscore(bowl['impact_rate'])
bowl['z_vol'] = zscore(np.log(bowl['balls_press']))
bowl['z_wickets'] = zscore(np.log(bowl['wickets_press'].clip(lower=1)))

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
top_bowlers = bowl.sort_values('pri_bowl_score', ascending=False).reset_index(drop=True)
top_bowlers['rank'] = top_bowlers.index + 1

print("\n=== REFINED TOP 15 BOWLERS UNDER PRESSURE ===")
print(top_bowlers[['rank', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press_raw', 'sr_press_raw', 'dot_pct_press', 'boundary_pct_press', 'impact_rate', 'pri_bowl_score']].head(15).to_string())


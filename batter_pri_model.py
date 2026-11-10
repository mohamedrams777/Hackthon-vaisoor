import os
import pandas as pd
import numpy as np

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

# Merge metadata
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

# Add Knockout weight multiplier: 1.25 for knockout balls, 1.0 otherwise
df['ball_weight'] = np.where(df['knock_out'] == 1, 1.25, 1.0)
df['is_ipl'] = df['comp_name'].str.contains('IPL', case=False, na=False)

# Let's inspect match-level consistency for batters
# For each player and match, compute pressure performance
batter_match = df[df['is_pressure']].groupby(['match_id', 'striker_id', 'striker_name']).agg(
    p_runs=('runs', 'sum'),
    p_balls=('runs', 'count'),
    p_dismissed=('is_wicket', 'sum'),
    p_weight=('ball_weight', 'mean')
).reset_index()
batter_match['p_sr'] = (batter_match['p_runs'] / batter_match['p_balls']) * 100
# A successful pressure match contribution: p_runs >= 20 and p_sr >= 135, OR p_runs >= 35
batter_match['is_impact_inning'] = ((batter_match['p_runs'] >= 20) & (batter_match['p_sr'] >= 135)) | (batter_match['p_runs'] >= 35)

batter_consistency = batter_match.groupby(['striker_id', 'striker_name']).agg(
    total_press_innings=('match_id', 'count'),
    impact_innings=('is_impact_inning', 'sum'),
    sr_std=('p_sr', 'std')
).reset_index()
batter_consistency['impact_rate'] = batter_consistency['impact_innings'] / batter_consistency['total_press_innings']

# Comprehensive Batter Analysis
overall_bat = df.groupby(['striker_id', 'striker_name']).agg(
    balls_all=('runs', 'count'),
    runs_all=('runs', 'sum'),
    dismissals_all=('is_wicket', 'sum')
).reset_index()
overall_bat['sr_base_all'] = (overall_bat['runs_all'] / overall_bat['balls_all']) * 100
overall_bat['avg_base_all'] = overall_bat['runs_all'] / overall_bat['dismissals_all'].replace(0, 1)

press_bat = df[df['is_pressure']].groupby(['striker_id', 'striker_name']).agg(
    balls_press=('runs', 'count'),
    weighted_balls_press=('ball_weight', 'sum'),
    runs_press=('runs', 'sum'),
    dismissals_press=('is_wicket', 'sum'),
    fours_press=('is_four', 'sum'),
    sixes_press=('is_six', 'sum'),
    dots_press=('runs', lambda x: (x == 0).sum()),
    matches_press=('match_id', 'nunique'),
    ko_balls_press=('knock_out', 'sum')
).reset_index()

bat = press_bat.merge(overall_bat, on=['striker_id', 'striker_name']).merge(batter_consistency, on=['striker_id', 'striker_name'])

# Filter minimum sample size: >= 150 pressure balls
bat = bat[bat['balls_press'] >= 150].copy()

# Rates
bat['sr_press'] = (bat['runs_press'] / bat['balls_press']) * 100
bat['avg_press'] = bat['runs_press'] / bat['dismissals_press'].replace(0, 0.5)
bat['boundary_pct_press'] = ((bat['fours_press'] + bat['sixes_press']) / bat['balls_press']) * 100
bat['dot_pct_press'] = (bat['dots_press'] / bat['balls_press']) * 100

# Non-pressure baseline
bat['balls_nonpress'] = bat['balls_all'] - bat['balls_press']
bat['runs_nonpress'] = bat['runs_all'] - bat['runs_press']
bat['dismissals_nonpress'] = bat['dismissals_all'] - bat['dismissals_press']
bat['sr_baseline'] = np.where(bat['balls_nonpress'] >= 50, (bat['runs_nonpress'] / bat['balls_nonpress']) * 100, bat['sr_base_all'])
bat['avg_baseline'] = np.where(bat['dismissals_nonpress'] > 0, bat['runs_nonpress'] / bat['dismissals_nonpress'], bat['avg_base_all'])

# Clutch deltas
bat['delta_sr'] = bat['sr_press'] - bat['sr_baseline']
bat['delta_avg'] = bat['avg_press'] - bat['avg_baseline']

# Now let's construct Batter Pressure Reliability Index (PRI_bat):
# Normalized sub-scores:
# 1. Scoring Velocity under pressure: z-score of sr_press vs league pressure par (139.65)
# 2. Dismissal Resistance: log(avg_press) z-score
# 3. Clutch Acceleration (Delta SR): z-score of delta_sr
# 4. Impact Consistency: impact_rate (% of pressure innings producing high impact)
# 5. Volume & Trust: log(balls_press)
from scipy.stats import zscore

bat['z_sr'] = zscore(bat['sr_press'])
bat['z_avg'] = zscore(np.log(bat['avg_press'].clip(lower=5)))
bat['z_delta_sr'] = zscore(bat['delta_sr'])
bat['z_boundary'] = zscore(bat['boundary_pct_press'])
bat['z_impact'] = zscore(bat['impact_rate'])
bat['z_vol'] = zscore(np.log(bat['balls_press']))

# Composite score (weights: SR 25%, Avg/Survival 20%, Delta SR 20%, Impact Consistency 20%, Volume/Trust 15%)
bat['pri_bat'] = (
    0.25 * bat['z_sr'] +
    0.20 * bat['z_avg'] +
    0.20 * bat['z_delta_sr'] +
    0.20 * bat['z_impact'] +
    0.15 * bat['z_vol']
)

# Rescale PRI to 0-100
min_p = bat['pri_bat'].min()
max_p = bat['pri_bat'].max()
bat['pri_bat_score'] = 50 + (bat['pri_bat'] / bat['pri_bat'].std()) * 15

print("=== TOP 20 BATTERS UNDER PRESSURE (PRI SCORE) ===")
top_bat = bat.sort_values('pri_bat_score', ascending=False).reset_index(drop=True)
top_bat['rank'] = top_bat.index + 1
print(top_bat[['rank', 'striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press', 'impact_rate', 'pri_bat_score']].head(20).to_string())


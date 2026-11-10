import os
import pandas as pd
import numpy as np
from scipy.stats import zscore

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

# Merge metadata
matches_info = matches[['match_id', 'comp_id', 'match_date', 'stage', 'knock_out', 'win_team_id', 'result', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']]
matches_info = matches_info.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

# Filter strictly to 2025-2026 matches
matches_info['year'] = pd.to_datetime(matches_info['match_date']).dt.year
m2526_info = matches_info[matches_info['year'].isin([2025, 2026])].copy()

df2526 = df.merge(m2526_info, on='match_id', how='inner')
print(f"2025-2026 Matches: {m2526_info['match_id'].nunique()}, Balls: {len(df2526)}")

df2526['is_legal_ball'] = ~df2526['extras_type'].isin(['wide', 'Overstep'])

def get_ball_team_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 1 if ext_type in ['wide', 'legbyes', 'byes', 'Overstep', 'other'] else 0
    return r + extras + ext2

df2526['ball_team_runs'] = df2526.apply(get_ball_team_runs, axis=1)

def get_bowler_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 1 if ext_type in ['wide', 'Overstep', 'other'] else 0
    return r + extras + ext2

df2526['bowler_runs'] = df2526.apply(get_bowler_runs, axis=1)
df2526['is_bowler_wicket'] = df2526['is_wicket'] & ~df2526['dismissal_type'].isin(['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field'])

df2526['cum_team_runs'] = df2526.groupby(['match_id', 'innings'])['ball_team_runs'].cumsum()
df2526['cum_wickets'] = df2526.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
df2526['legal_balls_bowled'] = df2526.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum()

# 1st innings total
inn1_totals = df2526[df2526['innings'] == 1].groupby('match_id')['cum_team_runs'].max().reset_index()
inn1_totals.rename(columns={'cum_team_runs': 'inn1_final_runs'}, inplace=True)
df2526 = df2526.merge(inn1_totals, on='match_id', how='left')

df2526['target'] = np.where(df2526['revised_target'].notna(), df2526['revised_target'], df2526['inn1_final_runs'] + 1)
df2526['runs_needed'] = df2526['target'] - df2526['cum_team_runs'] + df2526['ball_team_runs']
df2526['max_legal_balls'] = np.where(
    (df2526['innings'] == 1) & df2526['first_inn_revised_overs'].notna(), df2526['first_inn_revised_overs'] * 6,
    np.where((df2526['innings'] == 2) & df2526['second_inn_revised_overs'].notna(), df2526['second_inn_revised_overs'] * 6, 120)
)
df2526['balls_remaining'] = np.maximum(0, df2526['max_legal_balls'] - df2526['legal_balls_bowled'] + df2526['is_legal_ball'].astype(int))
df2526['wickets_in_hand'] = 10 - (df2526['cum_wickets'] - df2526['is_wicket'].astype(int))
df2526['rrr'] = np.where(df2526['balls_remaining'] > 0, df2526['runs_needed'] / (df2526['balls_remaining'] / 6.0), np.nan)

# Pressure definitions
p_inn2_death = (df2526['innings'] == 2) & (df2526['overid'] >= 15) & (df2526['runs_needed'] > 0) & (df2526['rrr'] >= 6.0) & (df2526['rrr'] <= 24.0) & (df2526['wickets_in_hand'] >= 1)
p_inn2_rrr = (df2526['innings'] == 2) & (df2526['overid'] >= 10) & (df2526['rrr'] >= 10.0) & (df2526['balls_remaining'] <= 66) & (df2526['wickets_in_hand'] >= 2) & (df2526['runs_needed'] > 0)
p_inn2_crisis = (df2526['innings'] == 2) & (df2526['overid'] <= 7) & (df2526['cum_wickets'] >= 3) & (df2526['rrr'] >= 8.5)

p_inn1_death = (df2526['innings'] == 1) & (df2526['overid'] >= 16)
p_inn1_crisis = (df2526['innings'] == 1) & (
    ((df2526['cum_wickets'] >= 3) & (df2526['overid'] <= 7) & (df2526['cum_team_runs'] <= 50)) |
    ((df2526['cum_wickets'] >= 4) & (df2526['overid'] <= 11) & (df2526['cum_team_runs'] <= 75))
)
p_super_over = df2526['innings'].isin([3, 4])

df2526['is_pressure'] = p_inn2_death | p_inn2_rrr | p_inn2_crisis | p_inn1_death | p_inn1_crisis | p_super_over
df2526['is_ipl'] = df2526['comp_name'].str.contains('IPL', case=False, na=False)

def get_phase(overid):
    if overid <= 6:
        return 'Powerplay'
    elif overid <= 15:
        return 'Middle'
    else:
        return 'Death'

df2526['phase'] = df2526['overid'].apply(get_phase)

# Context Par expectations in 2025-2026
comp_phase_stats = df2526[df2526['is_pressure']].groupby(['is_ipl', 'phase']).agg(
    exp_runs_per_ball=('bowler_runs', 'mean'),
    exp_wickets_per_ball=('is_bowler_wicket', 'mean'),
    exp_sr=('runs', lambda x: x.mean() * 100),
    exp_econ=('bowler_runs', lambda x: x.mean() * 6.0)
).reset_index()

df2526 = df2526.merge(comp_phase_stats[['is_ipl', 'phase', 'exp_runs_per_ball', 'exp_wickets_per_ball']], on=['is_ipl', 'phase'], how='left')

df2526['runs_saved_ball'] = df2526['exp_runs_per_ball'] - df2526['bowler_runs']
df2526['bat_runs_above_exp'] = df2526['runs'] - df2526['exp_runs_per_ball']

# League baselines 2025-2026
base_balls = df2526[~df2526['is_pressure']]
league_sr_base_2526 = (base_balls['runs'].sum() / len(base_balls)) * 100
league_econ_base_2526 = (base_balls['bowler_runs'].sum() / base_balls['is_legal_ball'].sum()) * 6.0

# ----------------- BATTERS 2025-2026 -----------------
overall_bat = df2526.groupby(['striker_id', 'striker_name']).agg(
    balls_all=('runs', 'count'),
    runs_all=('runs', 'sum'),
    dismissals_all=('is_wicket', 'sum')
).reset_index()

press_bat = df2526[df2526['is_pressure']].groupby(['striker_id', 'striker_name']).agg(
    balls_press=('runs', 'count'),
    runs_press=('runs', 'sum'),
    dismissals_press=('is_wicket', 'sum'),
    fours_press=('is_four', 'sum'),
    sixes_press=('is_six', 'sum'),
    dots_press=('runs', lambda x: (x == 0).sum()),
    matches_press=('match_id', 'nunique'),
    bat_runs_above_exp=('bat_runs_above_exp', 'sum')
).reset_index()

# Batter match consistency
batter_match = df2526[df2526['is_pressure']].groupby(['match_id', 'striker_id', 'striker_name']).agg(
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

# Sample size threshold for 2-year window: >= 100 pressure balls
bat = bat[bat['balls_press'] >= 100].copy()

bat['sr_press'] = (bat['runs_press'] / bat['balls_press']) * 100
bat['avg_press'] = bat['runs_press'] / bat['dismissals_press'].replace(0, 0.5)
bat['boundary_pct_press'] = ((bat['fours_press'] + bat['sixes_press']) / bat['balls_press']) * 100
bat['dot_pct_press'] = (bat['dots_press'] / bat['balls_press']) * 100
bat['rsaa_bat_per_100'] = (bat['bat_runs_above_exp'] / bat['balls_press']) * 100

bat['balls_nonpress'] = bat['balls_all'] - bat['balls_press']
bat['runs_nonpress'] = bat['runs_all'] - bat['runs_press']
bat['sr_base_reg'] = (bat['runs_nonpress'] + (60 * league_sr_base_2526 / 100.0)) / (bat['balls_nonpress'] + 60) * 100.0
bat['delta_sr'] = bat['sr_press'] - bat['sr_base_reg']

bat['z_rsab'] = zscore(bat['rsaa_bat_per_100'])
bat['z_avg'] = zscore(np.log(bat['avg_press'].clip(lower=5)))
bat['z_delta_sr'] = zscore(bat['delta_sr'])
bat['z_boundary'] = zscore(bat['boundary_pct_press'])
bat['z_impact'] = zscore(bat['impact_rate'])
bat['z_vol'] = zscore(np.log(bat['balls_press']))

bat['pri_bat'] = (
    0.25 * bat['z_rsab'] +
    0.20 * bat['z_avg'] +
    0.20 * bat['z_delta_sr'] +
    0.20 * bat['z_impact'] +
    0.15 * bat['z_vol']
)
bat['pri_bat_score'] = 50 + (bat['pri_bat'] / bat['pri_bat'].std()) * 15
top_20_bat = bat.sort_values('pri_bat_score', ascending=False).reset_index(drop=True).head(20)
top_20_bat['rank'] = top_20_bat.index + 1

# ----------------- BOWLERS 2025-2026 -----------------
overall_bowl = df2526.groupby(['bowler_id', 'bowler_name']).agg(
    balls_all=('is_legal_ball', 'sum'),
    runs_all=('bowler_runs', 'sum'),
    wickets_all=('is_bowler_wicket', 'sum')
).reset_index()

press_bowl = df2526[df2526['is_pressure']].groupby(['bowler_id', 'bowler_name']).agg(
    balls_press=('is_legal_ball', 'sum'),
    deliveries_press=('bowler_runs', 'count'),
    runs_press=('bowler_runs', 'sum'),
    wickets_press=('is_bowler_wicket', 'sum'),
    dots_press=('bowler_runs', lambda x: (x == 0).sum()),
    fours_press=('is_four', 'sum'),
    sixes_press=('is_six', 'sum'),
    matches_press=('match_id', 'nunique'),
    runs_saved_total=('runs_saved_ball', 'sum')
).reset_index()
press_bowl['boundaries_press'] = press_bowl['fours_press'] + press_bowl['sixes_press']

bowl_match = df2526[df2526['is_pressure']].groupby(['match_id', 'bowler_id', 'bowler_name']).agg(
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

# Sample size threshold for 2-year window: >= 100 pressure balls
bowl = bowl[bowl['balls_press'] >= 100].copy()

bowl['econ_press'] = (bowl['runs_press'] / bowl['balls_press']) * 6.0
bowl['sr_press'] = bowl['balls_press'] / bowl['wickets_press'].replace(0, 0.5)
bowl['dot_pct_press'] = (bowl['dots_press'] / bowl['deliveries_press']) * 100
bowl['boundary_pct_press'] = (bowl['boundaries_press'] / bowl['deliveries_press']) * 100
bowl['runs_saved_per_6'] = (bowl['runs_saved_total'] / bowl['balls_press']) * 6.0

bowl['z_rsaa'] = zscore(bowl['runs_saved_per_6'])
bowl['z_sr'] = -zscore(bowl['sr_press'])
bowl['z_dots'] = zscore(bowl['dot_pct_press'])
bowl['z_boundary_prev'] = -zscore(bowl['boundary_pct_press'])
bowl['z_impact'] = zscore(bowl['impact_rate'])
bowl['z_vol'] = zscore(np.log(bowl['balls_press']))
bowl['z_wickets'] = zscore(np.log(bowl['wickets_press'].clip(lower=1)))

bowl['pri_bowl'] = (
    0.25 * bowl['z_rsaa'] +
    0.15 * bowl['z_boundary_prev'] +
    0.15 * bowl['z_sr'] +
    0.10 * bowl['z_wickets'] +
    0.10 * bowl['z_dots'] +
    0.15 * bowl['z_impact'] +
    0.10 * bowl['z_vol']
)
bowl['pri_bowl_score'] = 50 + (bowl['pri_bowl'] / bowl['pri_bowl'].std()) * 15
top_20_bowl = bowl.sort_values('pri_bowl_score', ascending=False).reset_index(drop=True).head(20)
top_20_bowl['rank'] = top_20_bowl.index + 1

# Output directory: 2025-2026 folder
target_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\2025-2026'
os.makedirs(target_dir, exist_ok=True)

# Select relevant columns for export
cols_bat = ['rank', 'striker_id', 'striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press', 'dot_pct_press', 'rsaa_bat_per_100', 'impact_rate', 'pri_bat_score']
cols_bowl = ['rank', 'bowler_id', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'runs_saved_per_6', 'impact_rate', 'pri_bowl_score']

top_20_bat[cols_bat].to_csv(os.path.join(target_dir, 'top_20_batters_2025_2026.csv'), index=False)
top_20_bowl[cols_bowl].to_csv(os.path.join(target_dir, 'top_20_bowlers_2025_2026.csv'), index=False)

print("\n=== TOP 20 BATTERS IN 2025-2026 ===")
print(top_20_bat[['rank', 'striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press', 'impact_rate', 'pri_bat_score']].to_string())

print("\n=== TOP 20 BOWLERS IN 2025-2026 ===")
print(top_20_bowl[['rank', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'runs_saved_per_6', 'pri_bowl_score']].to_string())


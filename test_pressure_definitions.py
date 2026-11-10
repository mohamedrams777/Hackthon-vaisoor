import os
import pandas as pd
import numpy as np

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

# Let's inspect Innings 1 crisis and death
# Innings 1 crisis: wickets fallen >= 3 in over <= 7 and team score <= 50, OR wickets fallen >= 4 in over <= 12 and team score <= 80
df['is_inn1_crisis'] = (df['innings'] == 1) & (
    ((df['cum_wickets'] >= 3) & (df['overid'] <= 7) & (df['cum_team_runs'] <= 50)) |
    ((df['cum_wickets'] >= 4) & (df['overid'] <= 12) & (df['cum_team_runs'] <= 80))
)

# Innings 1 death overs: overid >= 16
df['is_inn1_death'] = (df['innings'] == 1) & (df['overid'] >= 16)

# Innings 2 pressure:
# Chasing death (overid >= 16) with game alive (runs_needed > 0 and rrr between 6.0 and 24.0)
df['is_inn2_death_close'] = (df['innings'] == 2) & (df['overid'] >= 16) & (df['runs_needed'] > 0) & (df['rrr'] >= 6.0) & (df['rrr'] <= 24.0) & (df['wickets_in_hand'] >= 1)

# Innings 2 high RRR: overid >= 11, rrr >= 10.0, wickets_in_hand >= 2, runs_needed > 0, balls_remaining <= 60
df['is_inn2_high_rrr'] = (df['innings'] == 2) & (df['overid'] >= 11) & (df['rrr'] >= 10.0) & (df['rrr'] <= 24.0) & (df['wickets_in_hand'] >= 2)

# Innings 2 crisis: wickets fallen >= 3 in over <= 7 with rrr >= 8.5
df['is_inn2_crisis'] = (df['innings'] == 2) & (df['cum_wickets'] >= 3) & (df['overid'] <= 7) & (df['rrr'] >= 8.5)

# Super overs (innings 3 or 4) are 100% extreme pressure
df['is_super_over'] = df['innings'].isin([3, 4])

# Knockout flag
df['is_knockout'] = df['knock_out'] == 1

print("Breakdown of pressure situations (number of balls):")
print(f"Inn 1 crisis: {df['is_inn1_crisis'].sum()}")
print(f"Inn 1 death: {df['is_inn1_death'].sum()}")
print(f"Inn 2 death close: {df['is_inn2_death_close'].sum()}")
print(f"Inn 2 high RRR: {df['is_inn2_high_rrr'].sum()}")
print(f"Inn 2 crisis: {df['is_inn2_crisis'].sum()}")
print(f"Super overs: {df['is_super_over'].sum()}")
print(f"Knockout balls: {df['is_knockout'].sum()}")


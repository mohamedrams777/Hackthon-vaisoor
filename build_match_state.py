import os
import pandas as pd
import numpy as np

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

# Merge match metadata
matches_info = matches[['match_id', 'comp_id', 'match_date', 'stage', 'knock_out', 'win_team_id', 'result', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']]
matches_info = matches_info.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

df = df.merge(matches_info, on='match_id', how='left')

# Sort chronologically by match, innings, over, ball
df['is_legal_ball'] = ~df['extras_type'].isin(['wide', 'Overstep'])

# Calculate total runs per ball for the team:
# runs off bat + 1 for wide + 1 for overstep + 1 for legbyes + 1 for byes + extras_2_runs
def get_ball_team_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 0
    if ext_type in ['wide', 'legbyes', 'byes']:
        extras += 1
    elif ext_type == 'Overstep':
        extras += 1
    elif ext_type == 'other':
        extras += 1
    return r + extras + ext2

df['ball_team_runs'] = df.apply(get_ball_team_runs, axis=1)

# Bowler runs conceded: runs off bat + wide + overstep + extras_2_runs (byes and legbyes don't count against bowler)
def get_bowler_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 0
    if ext_type in ['wide', 'Overstep', 'other']:
        extras += 1
    return r + extras + ext2

df['bowler_runs'] = df.apply(get_bowler_runs, axis=1)

# Bowler wicket: is_wicket == 1 and dismissal_type not in ['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field']
df['is_bowler_wicket'] = df['is_wicket'] & ~df['dismissal_type'].isin(['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field'])

# Group by match_id and innings to compute cumulative stats
df['cum_team_runs'] = df.groupby(['match_id', 'innings'])['ball_team_runs'].cumsum()
df['cum_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
df['legal_balls_bowled'] = df.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum()

# Get total 1st innings runs per match to find target for 2nd innings
inn1_totals = df[df['innings'] == 1].groupby('match_id')['cum_team_runs'].max().reset_index()
inn1_totals.rename(columns={'cum_team_runs': 'inn1_final_runs'}, inplace=True)
df = df.merge(inn1_totals, on='match_id', how='left')

# For 2nd innings, target is revised_target if present, else inn1_final_runs + 1
df['target'] = np.where(df['revised_target'].notna(), df['revised_target'], df['inn1_final_runs'] + 1)
df['runs_needed'] = np.where(df['innings'] == 2, df['target'] - df['cum_team_runs'] + df['ball_team_runs'], np.nan)

# Max legal balls in innings: default 120 (20 overs), or revised overs * 6
max_balls = np.where(
    (df['innings'] == 1) & df['first_inn_revised_overs'].notna(), df['first_inn_revised_overs'] * 6,
    np.where((df['innings'] == 2) & df['second_inn_revised_overs'].notna(), df['second_inn_revised_overs'] * 6, 120)
)
df['max_legal_balls'] = max_balls
df['balls_remaining'] = np.maximum(0, df['max_legal_balls'] - df['legal_balls_bowled'] + df['is_legal_ball'].astype(int))
df['wickets_in_hand'] = 10 - (df['cum_wickets'] - df['is_wicket'].astype(int))

# Required run rate for 2nd innings
df['rrr'] = np.where(
    (df['innings'] == 2) & (df['balls_remaining'] > 0),
    df['runs_needed'] / (df['balls_remaining'] / 6.0),
    np.nan
)

print("Sample innings 2 balls with RRR, runs_needed, balls_remaining, wickets_in_hand:")
print(df[df['innings'] == 2][['match_id', 'overid', 'over_ball_num', 'striker_name', 'cum_team_runs', 'runs_needed', 'balls_remaining', 'wickets_in_hand', 'rrr']].head(15))
print("\nRRR summary stats for innings 2:")
print(df[(df['innings'] == 2) & (df['balls_remaining'] >= 6)]['rrr'].describe())


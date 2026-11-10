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

# Let's compute batter stats: Overall vs Pressure
def compute_batter_metrics(min_press_balls=150):
    overall = df.groupby(['striker_id', 'striker_name']).agg(
        balls_all=('runs', 'count'),
        runs_all=('runs', 'sum'),
        dismissals_all=('is_wicket', 'sum'),
        fours_all=('is_four', 'sum'),
        sixes_all=('is_six', 'sum'),
        dots_all=('runs', lambda x: (x == 0).sum()),
        matches_all=('match_id', 'nunique')
    ).reset_index()
    
    press = df[df['is_pressure']].groupby(['striker_id', 'striker_name']).agg(
        balls_press=('runs', 'count'),
        runs_press=('runs', 'sum'),
        dismissals_press=('is_wicket', 'sum'),
        fours_press=('is_four', 'sum'),
        sixes_press=('is_six', 'sum'),
        dots_press=('runs', lambda x: (x == 0).sum()),
        matches_press=('match_id', 'nunique')
    ).reset_index()
    
    bat = overall.merge(press, on=['striker_id', 'striker_name'], how='inner')
    bat = bat[bat['balls_press'] >= min_press_balls].copy()
    
    # Non-pressure baseline
    bat['balls_base'] = bat['balls_all'] - bat['balls_press']
    bat['runs_base'] = bat['runs_all'] - bat['runs_press']
    bat['dismissals_base'] = bat['dismissals_all'] - bat['dismissals_press']
    bat['dots_base'] = bat['dots_all'] - bat['dots_press']
    bat['fours_base'] = bat['fours_all'] - bat['fours_press']
    bat['sixes_base'] = bat['sixes_all'] - bat['sixes_press']
    
    # Rates
    bat['sr_press'] = (bat['runs_press'] / bat['balls_press']) * 100
    bat['avg_press'] = bat['runs_press'] / bat['dismissals_press'].replace(0, 0.5)
    bat['boundary_pct_press'] = ((bat['fours_press'] + bat['sixes_press']) / bat['balls_press']) * 100
    bat['dot_pct_press'] = (bat['dots_press'] / bat['balls_press']) * 100
    
    bat['sr_base'] = np.where(bat['balls_base'] > 0, (bat['runs_base'] / bat['balls_base']) * 100, bat['sr_press'])
    bat['avg_base'] = np.where(bat['dismissals_base'] > 0, bat['runs_base'] / bat['dismissals_base'], bat['runs_base'])
    
    # Deltas
    bat['delta_sr'] = bat['sr_press'] - bat['sr_base']
    bat['delta_avg'] = bat['avg_press'] - bat['avg_base']
    
    return bat

# Let's compute bowler stats: Overall vs Pressure
def compute_bowler_metrics(min_press_balls=150):
    overall = df.groupby(['bowler_id', 'bowler_name']).agg(
        balls_all=('is_legal_ball', 'sum'),
        deliveries_all=('bowler_runs', 'count'),
        runs_all=('bowler_runs', 'sum'),
        wickets_all=('is_bowler_wicket', 'sum'),
        dots_all=('bowler_runs', lambda x: (x == 0).sum()),
        boundaries_all=('is_four', lambda x: x.sum()) # fours + sixes
    ).reset_index()
    # compute sixes conceded
    sixes_all = df[df['is_six']].groupby(['bowler_id', 'bowler_name']).size().reset_index(name='sixes_all')
    overall = overall.merge(sixes_all, on=['bowler_id', 'bowler_name'], how='left').fillna({'sixes_all': 0})
    overall['boundaries_all'] = overall['boundaries_all'] + overall['sixes_all']
    
    press = df[df['is_pressure']].groupby(['bowler_id', 'bowler_name']).agg(
        balls_press=('is_legal_ball', 'sum'),
        deliveries_press=('bowler_runs', 'count'),
        runs_press=('bowler_runs', 'sum'),
        wickets_press=('is_bowler_wicket', 'sum'),
        dots_press=('bowler_runs', lambda x: (x == 0).sum()),
        fours_press=('is_four', 'sum'),
        sixes_press=('is_six', 'sum'),
        matches_press=('match_id', 'nunique')
    ).reset_index()
    press['boundaries_press'] = press['fours_press'] + press['sixes_press']
    
    bowl = overall.merge(press, on=['bowler_id', 'bowler_name'], how='inner')
    bowl = bowl[bowl['balls_press'] >= min_press_balls].copy()
    
    bowl['balls_base'] = bowl['balls_all'] - bowl['balls_press']
    bowl['runs_base'] = bowl['runs_all'] - bowl['runs_press']
    bowl['wickets_base'] = bowl['wickets_all'] - bowl['wickets_press']
    
    bowl['econ_press'] = (bowl['runs_press'] / bowl['balls_press']) * 6.0
    bowl['sr_press'] = np.where(bowl['wickets_press'] > 0, bowl['balls_press'] / bowl['wickets_press'], np.nan)
    bowl['avg_press'] = np.where(bowl['wickets_press'] > 0, bowl['runs_press'] / bowl['wickets_press'], np.nan)
    bowl['dot_pct_press'] = (bowl['dots_press'] / bowl['deliveries_press']) * 100
    bowl['boundary_pct_press'] = (bowl['boundaries_press'] / bowl['deliveries_press']) * 100
    
    bowl['econ_base'] = np.where(bowl['balls_base'] > 0, (bowl['runs_base'] / bowl['balls_base']) * 6.0, bowl['econ_press'])
    bowl['delta_econ'] = bowl['econ_base'] - bowl['econ_press'] # Positive means improved under pressure
    
    return bowl

batters = compute_batter_metrics(150)
bowlers = compute_bowler_metrics(150)

print(f"Qualified batters (>=150 press balls): {len(batters)}")
print(f"Qualified bowlers (>=150 press balls): {len(bowlers)}")

print("\n--- Top Batters by Pressure Strike Rate (min 150 press balls) ---")
print(batters.sort_values('sr_press', ascending=False)[['striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press']].head(15))

print("\n--- Top Batters by Pressure Average (min 150 press balls) ---")
print(batters.sort_values('avg_press', ascending=False)[['striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_avg', 'boundary_pct_press']].head(15))

print("\n--- Top Bowlers by Pressure Economy (min 150 press balls) ---")
print(bowlers.sort_values('econ_press')[['bowler_name', 'balls_press', 'runs_press', 'wickets_press', 'econ_press', 'sr_press', 'delta_econ', 'dot_pct_press']].head(15))

print("\n--- Top Bowlers by Pressure Wickets (min 150 press balls) ---")
print(bowlers.sort_values('wickets_press', ascending=False)[['bowler_name', 'balls_press', 'runs_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press']].head(15))


import os
import pandas as pd

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))

sample_match_ids = [13511, 13512, 13513, 13514, 13515]
for mid in sample_match_ids:
    m = matches[matches['match_id'] == mid].iloc[0]
    print(f"Match {mid}: {m['home_team']} vs {m['away_team']}, Result: {m['result']}")
    m_df = df[df['match_id'] == mid]
    for inn in sorted(m_df['innings'].unique()):
        inn_df = m_df[m_df['innings'] == inn]
        bat_runs = inn_df['runs'].sum()
        wides = (inn_df['extras_type'] == 'wide').sum()
        noballs = (inn_df['extras_type'] == 'Overstep').sum()
        legbyes = (inn_df['extras_type'] == 'legbyes').sum()
        byes = (inn_df['extras_type'] == 'byes').sum()
        extras2 = inn_df['extras_2_runs'].sum()
        wickets = inn_df['is_wicket'].sum()
        legal_balls = len(inn_df[~inn_df['extras_type'].isin(['wide', 'Overstep'])])
        overs = f"{legal_balls // 6}.{legal_balls % 6}"
        total_runs = bat_runs + wides + noballs + legbyes + byes + extras2
        print(f"  Inn {inn}: Bat {bat_runs} + Wides {wides} + NB {noballs} + LB {legbyes} + B {byes} + Ext2 {extras2} = Total {total_runs}/{wickets} in {overs} ov")


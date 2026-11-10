import pandas as pd
from bowler_pri_model import df, top_bowl

print('--- Top Bowlers: IPL vs T20I Balls & Competitions ---')
for idx, r in top_bowl.head(20).iterrows():
    bname = r['bowler_name']
    b_df = df[(df['bowler_name'] == bname) & (df['is_pressure'])]
    is_ipl = b_df['comp_name'].str.contains('IPL', case=False, na=False)
    ipl_balls = b_df[is_ipl]['is_legal_ball'].sum()
    t20i_balls = b_df[~is_ipl]['is_legal_ball'].sum()
    comps_played = b_df['comp_name'].unique().tolist()
    print(f"{bname:22s} | Total: {r['balls_press']:4d} | IPL: {ipl_balls:4d} | T20I: {t20i_balls:4d} | Econ: {r['econ_press']:.2f} | Wkts: {r['wickets_press']:2d} | Comps: {len(comps_played)}")
    print(f"   Comps: {comps_played[:4]}")

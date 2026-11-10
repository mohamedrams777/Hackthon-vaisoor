import pandas as pd
from batter_pri_model import df, top_bat

print('--- Top Batters: IPL vs T20I Balls & Competitions ---')
for idx, r in top_bat.head(20).iterrows():
    sname = r['striker_name']
    s_df = df[(df['striker_name'] == sname) & (df['is_pressure'])]
    is_ipl = s_df['comp_name'].str.contains('IPL', case=False, na=False)
    ipl_balls = len(s_df[is_ipl])
    t20i_balls = len(s_df[~is_ipl])
    comps_played = s_df['comp_name'].unique().tolist()
    print(f"{sname:22s} | Total: {r['balls_press']:4d} | IPL: {ipl_balls:4d} | T20I: {t20i_balls:4d} | SR: {r['sr_press']:.1f} | Avg: {r['avg_press']:.1f} | Delta SR: +{r['delta_sr']:.1f} | Comps: {len(comps_played)}")


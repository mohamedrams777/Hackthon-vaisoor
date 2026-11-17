import pandas as pd

df_map = pd.read_csv('data/competition_team_player_mapping.csv')
bat = pd.read_csv('all_qualified_batters_pressure_rankings.csv')
bowl = pd.read_csv('all_qualified_bowlers_pressure_rankings.csv')

pak_players = set(df_map[df_map['team_name'].str.contains('Pakistan', case=False, na=False)]['player_name'].dropna().unique())

ipl_comps = [1358, 1715, 2193, 2725, 3298]
ipl_map = df_map[df_map['comp_id'].isin(ipl_comps)]
other_ipl_teams = set(ipl_map['team_name'].unique()) - {'Rajasthan Royals'}

player_ipl_teams_all = ipl_map.groupby('player_name')['team_name'].unique().to_dict()

# STRICT FILTER:
# Either:
# 1) Player ONLY played for Rajasthan Royals (never for any other IPL franchise)
# 2) Player has NO IPL franchise (Pure International Free Agent)
# AND not in Pakistan

def get_strict_pool(df, ptype='bat'):
    pcol = 'striker_name' if ptype == 'bat' else 'bowler_name'
    score_col = 'pri_bat_score' if ptype == 'bat' else 'pri_bowl_score'
    
    valid = df[~df[pcol].isin(pak_players)].copy()
    
    results = []
    for _, row in valid.iterrows():
        name = row[pcol]
        teams = set(player_ipl_teams_all.get(name, []))
        
        has_other = bool(teams.intersection(other_ipl_teams))
        is_rr = 'Rajasthan Royals' in teams
        
        if not has_other:
            # Either pure RR or pure Free Agent
            category = 'Rajasthan Royals (Pure)' if is_rr else 'Pure Free Agent (Intl)'
            row_dict = row.to_dict()
            row_dict['category'] = category
            results.append(row_dict)
            
    res_df = pd.DataFrame(results)
    return res_df.sort_values(score_col, ascending=False).reset_index(drop=True)

bat_strict = get_strict_pool(bat, 'bat')
bowl_strict = get_strict_pool(bowl, 'bowl')

print("=== STRICT FILTER: BATTERS (ONLY RR + PURE FREE AGENTS) ===")
cols_b = ['striker_name', 'category', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'pri_bat_score']
print(bat_strict[cols_b].to_string())

print("\n=== STRICT FILTER: BOWLERS (ONLY RR + PURE FREE AGENTS) ===")
cols_bw = ['bowler_name', 'category', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'pri_bowl_score']
print(bowl_strict[cols_bw].to_string())


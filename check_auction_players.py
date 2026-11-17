import pandas as pd

df_map = pd.read_csv('data/competition_team_player_mapping.csv')
bat = pd.read_csv('all_qualified_batters_pressure_rankings.csv')
bowl = pd.read_csv('all_qualified_bowlers_pressure_rankings.csv')

# Exclude Pakistan players
pak_players = set(df_map[df_map['team_name'].str.contains('Pakistan', case=False, na=False)]['player_name'].dropna().unique())

ipl_comps = [1358, 1715, 2193, 2725, 3298]
ipl_map = df_map[df_map['comp_id'].isin(ipl_comps)]
other_ipl_teams = set(ipl_map['team_name'].unique()) - {'Rajasthan Royals'}

player_ipl_teams_all = ipl_map.groupby('player_name')['team_name'].unique().to_dict()
player_ipl_teams_2026 = ipl_map[ipl_map['comp_id'] == 3298].groupby('player_name')['team_name'].unique().to_dict()

print('=== TOP 40 BATTERS & THEIR IPL TEAMS ===')
for idx, row in bat.head(40).iterrows():
    name = row['striker_name']
    is_pak = name in pak_players
    teams_all = list(player_ipl_teams_all.get(name, ['No IPL Team']))
    teams_26 = list(player_ipl_teams_2026.get(name, ['No IPL Team (2026)']))
    is_rr = 'Rajasthan Royals' in teams_all
    in_other_all = any(t in other_ipl_teams for t in teams_all)
    in_other_26 = any(t in other_ipl_teams for t in teams_26)
    
    status_all = "RR" if is_rr and not in_other_all else ("RR+Other" if is_rr else ("Other IPL" if in_other_all else "FREE AGENT"))
    print(f"{row['rank']:2d}. {name:25s} | PRI: {row['pri_bat_score']:.1f} | Pak: {is_pak!s:5s} | Status: {status_all:11s} | 2026: {teams_26}")


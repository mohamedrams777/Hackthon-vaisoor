import pandas as pd

df_map = pd.read_csv('data/competition_team_player_mapping.csv')
bat = pd.read_csv('all_qualified_batters_pressure_rankings.csv')
bowl = pd.read_csv('all_qualified_bowlers_pressure_rankings.csv')

pak_players = set(df_map[df_map['team_name'].str.contains('Pakistan', case=False, na=False)]['player_name'].dropna().unique())

ipl_comps = [1358, 1715, 2193, 2725, 3298]
ipl_map = df_map[df_map['comp_id'].isin(ipl_comps)]
other_ipl_teams = set(ipl_map['team_name'].unique()) - {'Rajasthan Royals'}

player_ipl_teams_all = ipl_map.groupby('player_name')['team_name'].unique().to_dict()
player_ipl_teams_2026 = ipl_map[ipl_map['comp_id'] == 3298].groupby('player_name')['team_name'].unique().to_dict()

# Let's filter batters
valid_bat = bat[~bat['striker_name'].isin(pak_players)].copy()

def get_auction_status(name):
    teams_all = list(player_ipl_teams_all.get(name, []))
    teams_26 = list(player_ipl_teams_2026.get(name, []))
    is_rr_26 = 'Rajasthan Royals' in teams_26
    is_rr_all = 'Rajasthan Royals' in teams_all
    in_other_26 = any(t in other_ipl_teams for t in teams_26)
    in_other_all = any(t in other_ipl_teams for t in teams_all)
    
    if is_rr_26:
        return 'RR Squad (2026)'
    elif is_rr_all and not in_other_26:
        return 'RR Ex-Player / Free Agent'
    elif is_rr_all and in_other_26:
        return f'RR Alumni (Contracted to {teams_26[0]})'
    elif not teams_all:
        return 'Pure Free Agent (Intl)'
    elif not in_other_26:
        return 'Available Free Agent / Released'
    else:
        return f'Contracted to {teams_26[0]}'

valid_bat['auction_status'] = valid_bat['striker_name'].apply(get_auction_status)
valid_bat['teams_all'] = valid_bat['striker_name'].apply(lambda n: ", ".join(player_ipl_teams_all.get(n, ['Free Agent'])))
valid_bat['teams_2026'] = valid_bat['striker_name'].apply(lambda n: ", ".join(player_ipl_teams_2026.get(n, ['Uncontracted / Free Agent'])))

# Filter for: In RR or NOT contracted to other IPL teams in 2026
avail_bat_2026 = valid_bat[~valid_bat['auction_status'].str.startswith('Contracted to')].copy()
avail_bat_2026 = avail_bat_2026.sort_values('pri_bat_score', ascending=False).reset_index(drop=True)
avail_bat_2026['auction_rank'] = range(1, len(avail_bat_2026) + 1)

print("TOP 20 BATTERS (AVAILABLE FOR AUCTION + RR PLAYERS):")
cols_b = ['auction_rank', 'striker_name', 'auction_status', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'pri_bat_score']
print(avail_bat_2026[cols_b].head(20).to_string())

# Bowlers
valid_bowl = bowl[~bowl['bowler_name'].isin(pak_players)].copy()
valid_bowl['auction_status'] = valid_bowl['bowler_name'].apply(get_auction_status)
valid_bowl['teams_all'] = valid_bowl['bowler_name'].apply(lambda n: ", ".join(player_ipl_teams_all.get(n, ['Free Agent'])))
valid_bowl['teams_2026'] = valid_bowl['bowler_name'].apply(lambda n: ", ".join(player_ipl_teams_2026.get(n, ['Uncontracted / Free Agent'])))

avail_bowl_2026 = valid_bowl[~valid_bowl['auction_status'].str.startswith('Contracted to')].copy()
avail_bowl_2026 = avail_bowl_2026.sort_values('pri_bowl_score', ascending=False).reset_index(drop=True)
avail_bowl_2026['auction_rank'] = range(1, len(avail_bowl_2026) + 1)

print("\nTOP 20 BOWLERS (AVAILABLE FOR AUCTION + RR PLAYERS):")
cols_bowl = ['auction_rank', 'bowler_name', 'auction_status', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'pri_bowl_score']
print(avail_bowl_2026[cols_bowl].head(20).to_string())

# Save to CSV for reference and web usage
avail_bat_2026.head(20).to_csv('rr_auction_top_20_batters.csv', index=False)
avail_bowl_2026.head(20).to_csv('rr_auction_top_20_bowlers.csv', index=False)


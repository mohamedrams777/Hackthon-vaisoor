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

def analyze_pool(df, ptype='bat'):
    pcol = 'striker_name' if ptype == 'bat' else 'bowler_name'
    score_col = 'pri_bat_score' if ptype == 'bat' else 'pri_bowl_score'
    
    # Filter out Pakistan players
    valid_df = df[~df[pcol].isin(pak_players)].copy()
    
    # Interpretation 1: Never played for any other IPL team (all-time 2022-2026).
    # Allowed: RR only, OR No IPL team at all
    def is_eligible_strict(name):
        teams = set(player_ipl_teams_all.get(name, []))
        # Not in any other IPL team
        if teams.intersection(other_ipl_teams):
            return False
        return True

    # Interpretation 1b: Has played for RR (ever) OR No IPL team at all (never in other IPL team)
    def is_eligible_rr_or_free(name):
        teams = set(player_ipl_teams_all.get(name, []))
        if 'Rajasthan Royals' in teams:
            return True
        if not teams.intersection(other_ipl_teams):
            return True
        return False

    # Interpretation 2: Not in any other IPL team in 2026 (available in auction or in RR)
    def is_eligible_2026(name):
        teams_26 = set(player_ipl_teams_2026.get(name, []))
        other_in_26 = teams_26.intersection(other_ipl_teams)
        if other_in_26:
            return False
        return True

    print(f"\n==================== {ptype.upper()} POOL ANALYSIS ====================")
    pool1 = valid_df[valid_df[pcol].apply(is_eligible_strict)].copy()
    print(f"Pool 1 (Strict: Never in other IPL team, only RR or Pure Free Agent): {len(pool1)} players")
    for r, (_, row) in enumerate(pool1.head(25).iterrows(), 1):
        teams = list(player_ipl_teams_all.get(row[pcol], ['Free Agent']))
        print(f"  {r:2d}. {row[pcol]:25s} | PRI: {row[score_col]:.2f} | Teams: {teams}")

    pool1b = valid_df[valid_df[pcol].apply(is_eligible_rr_or_free)].copy()
    print(f"\nPool 1b (Played for RR [even if also played for other team] OR Pure Free Agent): {len(pool1b)} players")
    for r, (_, row) in enumerate(pool1b.head(25).iterrows(), 1):
        teams = list(player_ipl_teams_all.get(row[pcol], ['Free Agent']))
        print(f"  {r:2d}. {row[pcol]:25s} | PRI: {row[score_col]:.2f} | Teams: {teams}")

    pool2 = valid_df[valid_df[pcol].apply(is_eligible_2026)].copy()
    print(f"\nPool 2 (Auction 2026: In RR 2026 OR Not in any IPL team in 2026): {len(pool2)} players")
    for r, (_, row) in enumerate(pool2.head(25).iterrows(), 1):
        teams_26 = list(player_ipl_teams_2026.get(row[pcol], ['Free Agent 2026']))
        teams_all = list(player_ipl_teams_all.get(row[pcol], ['Free Agent']))
        print(f"  {r:2d}. {row[pcol]:25s} | PRI: {row[score_col]:.2f} | 2026: {teams_26} | All: {teams_all}")

analyze_pool(bat, 'bat')
analyze_pool(bowl, 'bowl')


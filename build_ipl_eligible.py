import os
import pandas as pd

# 1. Identify Pakistan players
ctpm = pd.read_csv('data/competition_team_player_mapping.csv')
pak_players = set(ctpm[ctpm['team_name'].str.contains('Pakistan', case=False, na=False)]['player_name'].unique())
print(f"Total Pakistan players identified: {len(pak_players)}")

# Output folder
out_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\only ipl eligible'
os.makedirs(out_dir, exist_ok=True)

# 2. Overall 2022-2026 (From full model)
from compute_context_adjusted_rankings import top_bat, top_bowl

# Filter batters
bat_ipl = top_bat[~top_bat['striker_name'].isin(pak_players)].copy().reset_index(drop=True)
bat_ipl['rank'] = bat_ipl.index + 1

# Filter bowlers
bowl_ipl = top_bowl[~top_bowl['bowler_name'].isin(pak_players)].copy().reset_index(drop=True)
bowl_ipl['rank'] = bowl_ipl.index + 1

# Save Overall 2022-2026 IPL Eligible
cols_bat = ['rank', 'striker_id', 'striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press', 'dot_pct_press', 'rsaa_bat_per_100', 'impact_rate', 'pri_bat_score']
cols_bowl = ['rank', 'bowler_id', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'runs_saved_per_6', 'impact_rate', 'pri_bowl_score']

bat_ipl.head(10)[cols_bat].to_csv(os.path.join(out_dir, 'top_10_batters_ipl_eligible.csv'), index=False)
bowl_ipl.head(10)[cols_bowl].to_csv(os.path.join(out_dir, 'top_10_bowlers_ipl_eligible.csv'), index=False)

bat_ipl.head(20)[cols_bat].to_csv(os.path.join(out_dir, 'top_20_batters_ipl_eligible.csv'), index=False)
bowl_ipl.head(20)[cols_bowl].to_csv(os.path.join(out_dir, 'top_20_bowlers_ipl_eligible.csv'), index=False)

print("\n=== TOP 10 BOWLERS (IPL ELIGIBLE - 2022-2026) ===")
print(bowl_ipl.head(10)[['rank', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'runs_saved_per_6', 'pri_bowl_score']].to_string())

# 3. 2025-2026 Season IPL Eligible
dir_2526 = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\2025-2026'
bat_2526 = pd.read_csv(os.path.join(dir_2526, 'top_20_batters_2025_2026.csv'))
bowl_2526 = pd.read_csv(os.path.join(dir_2526, 'top_20_bowlers_2025_2026.csv'))

# Load full qualified list for 2025-2026 to ensure we get a full top 20 after removing Pakistan players
from build_2025_2026_rankings import bat as bat_2526_full, bowl as bowl_2526_full

bat_2526_ipl = bat_2526_full[~bat_2526_full['striker_name'].isin(pak_players)].sort_values('pri_bat_score', ascending=False).reset_index(drop=True).head(20)
bat_2526_ipl['rank'] = bat_2526_ipl.index + 1

bowl_2526_ipl = bowl_2526_full[~bowl_2526_full['bowler_name'].isin(pak_players)].sort_values('pri_bowl_score', ascending=False).reset_index(drop=True).head(20)
bowl_2526_ipl['rank'] = bowl_2526_ipl.index + 1

bat_2526_ipl[cols_bat].to_csv(os.path.join(out_dir, 'top_20_batters_2025_2026_ipl_eligible.csv'), index=False)
bowl_2526_ipl[cols_bowl].to_csv(os.path.join(out_dir, 'top_20_bowlers_2025_2026_ipl_eligible.csv'), index=False)

print("\n=== TOP 20 BOWLERS (IPL ELIGIBLE - 2025-2026) ===")
print(bowl_2526_ipl[['rank', 'bowler_name', 'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'dot_pct_press', 'boundary_pct_press', 'runs_saved_per_6', 'pri_bowl_score']].to_string())

print("\n=== TOP 20 BATTERS (IPL ELIGIBLE - 2025-2026) ===")
print(bat_2526_ipl[['rank', 'striker_name', 'balls_press', 'runs_press', 'sr_press', 'avg_press', 'delta_sr', 'boundary_pct_press', 'pri_bat_score']].to_string())


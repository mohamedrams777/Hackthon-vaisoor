import os
import sys
import pandas as pd
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'superr_selector.settings')
django.setup()

from pressure_app.models import BatterRanking, BowlerRanking, MatchSummary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def get_pakistan_players():
    # Identify Pakistan players from mapping file
    mapping_path = os.path.join(DATA_DIR, 'competition_team_player_mapping.csv')
    if not os.path.exists(mapping_path):
        return set()
    df_map = pd.read_csv(mapping_path)
    pak_mask = df_map['team_name'].str.contains('Pakistan', case=False, na=False)
    pak_players = set(df_map[pak_mask]['player_name'].dropna().unique())
    return pak_players

def load_batters():
    print("Loading Batters...")
    pak_players = get_pakistan_players()
    
    # 1. All qualified batters (2022-2026)
    all_bat_path = os.path.join(BASE_DIR, 'all_qualified_batters_pressure_rankings.csv')
    if os.path.exists(all_bat_path):
        df_all = pd.read_csv(all_bat_path)
        for _, row in df_all.iterrows():
            name = str(row['striker_name'])
            is_ipl = name not in pak_players
            BatterRanking.objects.create(
                striker_id=int(row.get('striker_id', 0)),
                striker_name=name,
                season_category='all_2022_2026',
                is_ipl_eligible=is_ipl,
                rank=int(row.get('rank', 0)),
                balls_press=int(row.get('balls_press', 0)),
                runs_press=int(row.get('runs_press', 0)),
                sr_press=float(row.get('sr_press', 0.0)),
                avg_press=float(row.get('avg_press', 0.0)),
                delta_sr=float(row.get('delta_sr', 0.0)),
                boundary_pct_press=float(row.get('boundary_pct_press', 0.0)),
                dot_pct_press=float(row.get('dot_pct_press', 0.0)),
                rsaa_bat_per_100=float(row.get('rsaa_bat_per_100', 0.0)),
                impact_rate=float(row.get('impact_rate', 0.0)),
                pri_bat_score=float(row.get('pri_bat_score', 0.0))
            )
        print(f"Loaded {len(df_all)} all-time batters.")

    # 2. 2025-2026 batters
    bat_2526_path = os.path.join(BASE_DIR, '2025-2026', 'top_20_batters_2025_2026.csv')
    if os.path.exists(bat_2526_path):
        df_2526 = pd.read_csv(bat_2526_path)
        for _, row in df_2526.iterrows():
            name = str(row['striker_name'])
            is_ipl = name not in pak_players
            BatterRanking.objects.create(
                striker_id=int(row.get('striker_id', 0)),
                striker_name=name,
                season_category='recent_2025_2026',
                is_ipl_eligible=is_ipl,
                rank=int(row.get('rank', 0)),
                balls_press=int(row.get('balls_press', 0)),
                runs_press=int(row.get('runs_press', 0)),
                sr_press=float(row.get('sr_press', 0.0)),
                avg_press=float(row.get('avg_press', 0.0)),
                delta_sr=float(row.get('delta_sr', 0.0)),
                boundary_pct_press=float(row.get('boundary_pct_press', 0.0)),
                dot_pct_press=float(row.get('dot_pct_press', 0.0)),
                rsaa_bat_per_100=float(row.get('rsaa_bat_per_100', 0.0)),
                impact_rate=float(row.get('impact_rate', 0.0)),
                pri_bat_score=float(row.get('pri_bat_score', 0.0))
            )
        print(f"Loaded {len(df_2526)} 2025-2026 batters.")

def load_bowlers():
    print("Loading Bowlers...")
    pak_players = get_pakistan_players()

    # 1. All qualified bowlers (2022-2026)
    all_bowl_path = os.path.join(BASE_DIR, 'all_qualified_bowlers_pressure_rankings.csv')
    if os.path.exists(all_bowl_path):
        df_all = pd.read_csv(all_bowl_path)
        for _, row in df_all.iterrows():
            name = str(row['bowler_name'])
            is_ipl = name not in pak_players
            BowlerRanking.objects.create(
                bowler_id=int(row.get('bowler_id', 0)),
                bowler_name=name,
                season_category='all_2022_2026',
                is_ipl_eligible=is_ipl,
                rank=int(row.get('rank', 0)),
                balls_press=int(row.get('balls_press', 0)),
                wickets_press=int(row.get('wickets_press', 0)),
                econ_press=float(row.get('econ_press', 0.0)),
                sr_press=float(row.get('sr_press', 0.0)),
                dot_pct_press=float(row.get('dot_pct_press', 0.0)),
                boundary_pct_press=float(row.get('boundary_pct_press', 0.0)),
                runs_saved_per_6=float(row.get('runs_saved_per_6', 0.0)),
                impact_rate=float(row.get('impact_rate', 0.0)),
                pri_bowl_score=float(row.get('pri_bowl_score', 0.0))
            )
        print(f"Loaded {len(df_all)} all-time bowlers.")

    # 2. 2025-2026 bowlers
    bowl_2526_path = os.path.join(BASE_DIR, '2025-2026', 'top_20_bowlers_2025_2026.csv')
    if os.path.exists(bowl_2526_path):
        df_2526 = pd.read_csv(bowl_2526_path)
        for _, row in df_2526.iterrows():
            name = str(row['bowler_name'])
            is_ipl = name not in pak_players
            BowlerRanking.objects.create(
                bowler_id=int(row.get('bowler_id', 0)),
                bowler_name=name,
                season_category='recent_2025_2026',
                is_ipl_eligible=is_ipl,
                rank=int(row.get('rank', 0)),
                balls_press=int(row.get('balls_press', 0)),
                wickets_press=int(row.get('wickets_press', 0)),
                econ_press=float(row.get('econ_press', 0.0)),
                sr_press=float(row.get('sr_press', 0.0)),
                dot_pct_press=float(row.get('dot_pct_press', 0.0)),
                boundary_pct_press=float(row.get('boundary_pct_press', 0.0)),
                runs_saved_per_6=float(row.get('runs_saved_per_6', 0.0)),
                impact_rate=float(row.get('impact_rate', 0.0)),
                pri_bowl_score=float(row.get('pri_bowl_score', 0.0))
            )
        print(f"Loaded {len(df_2526)} 2025-2026 bowlers.")

def load_matches():
    print("Loading Matches...")
    matches_csv = os.path.join(DATA_DIR, 'matches.csv')
    comps_csv = os.path.join(DATA_DIR, 'competitions.csv')
    
    if not os.path.exists(matches_csv) or not os.path.exists(comps_csv):
        print("Matches or competitions CSV not found.")
        return

    df_matches = pd.read_csv(matches_csv)
    df_comps = pd.read_csv(comps_csv)
    
    df_merged = df_matches.merge(df_comps[['comp_id', 'comp_name', 'match_format']], on='comp_id', how='left')
    
    match_objs = []
    for _, row in df_merged.iterrows():
        comp_name = str(row.get('comp_name', ''))
        is_ipl = 'IPL' in comp_name.upper()
        
        match_objs.append(MatchSummary(
            match_id=int(row['match_id']),
            comp_id=int(row.get('comp_id', 0)),
            comp_name=comp_name,
            match_date=str(row.get('match_date', ''))[:50],
            stage=str(row.get('stage', ''))[:100],
            home_team=str(row.get('home_team', ''))[:100],
            away_team=str(row.get('away_team', ''))[:100],
            result=str(row.get('result', ''))[:250],
            knock_out=bool(row.get('knock_out', False)),
            is_ipl=is_ipl
        ))

    MatchSummary.objects.bulk_create(match_objs, ignore_conflicts=True)
    print(f"Loaded {len(match_objs)} matches.")

def main():
    print("Flushing existing records...")
    BatterRanking.objects.all().delete()
    BowlerRanking.objects.all().delete()
    MatchSummary.objects.all().delete()

    load_batters()
    load_bowlers()
    load_matches()
    print("All data successfully seeded into database!")

if __name__ == '__main__':
    main()


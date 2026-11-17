import os
import pandas as pd
from django.shortcuts import render, get_object_or_404
from .models import BatterRanking, BowlerRanking, MatchSummary
from django.db.models import Q
from django.conf import settings

def home(request):
    top_batters = BatterRanking.objects.filter(season_category='all_2022_2026', is_ipl_eligible=False).order_by('rank')[:10]
    if not top_batters.exists():
        top_batters = BatterRanking.objects.filter(season_category='all_2022_2026').order_by('rank')[:10]

    top_bowlers = BowlerRanking.objects.filter(season_category='all_2022_2026', is_ipl_eligible=False).order_by('rank')[:10]
    if not top_bowlers.exists():
        top_bowlers = BowlerRanking.objects.filter(season_category='all_2022_2026').order_by('rank')[:10]

    total_matches = MatchSummary.objects.count()
    ipl_matches = MatchSummary.objects.filter(is_ipl=True).count()
    ko_matches = MatchSummary.objects.filter(knock_out=True).count()

    context = {
        'top_batters': top_batters,
        'top_bowlers': top_bowlers,
        'total_matches': total_matches,
        'ipl_matches': ipl_matches,
        'ko_matches': ko_matches,
    }
    return render(request, 'pressure_app/index.html', context)

def batters_view(request):
    query = request.GET.get('q', '').strip()
    season = request.GET.get('season', 'all_2022_2026')
    eligible_only = request.GET.get('ipl_only', 'false') == 'true'

    batters = BatterRanking.objects.filter(season_category=season)
    if eligible_only:
        batters = batters.filter(is_ipl_eligible=True)
    if query:
        batters = batters.filter(striker_name__icontains=query)

    batters = batters.order_by('rank')

    context = {
        'batters': batters,
        'query': query,
        'season': season,
        'ipl_only': eligible_only,
    }
    return render(request, 'pressure_app/batters.html', context)

def bowlers_view(request):
    query = request.GET.get('q', '').strip()
    season = request.GET.get('season', 'all_2022_2026')
    eligible_only = request.GET.get('ipl_only', 'false') == 'true'

    bowlers = BowlerRanking.objects.filter(season_category=season)
    if eligible_only:
        bowlers = bowlers.filter(is_ipl_eligible=True)
    if query:
        bowlers = bowlers.filter(bowler_name__icontains=query)

    bowlers = bowlers.order_by('rank')

    context = {
        'bowlers': bowlers,
        'query': query,
        'season': season,
        'ipl_only': eligible_only,
    }
    return render(request, 'pressure_app/bowlers.html', context)

def ipl_eligible_view(request):
    batters = BatterRanking.objects.filter(season_category='all_2022_2026', is_ipl_eligible=True).order_by('rank')[:20]
    bowlers = BowlerRanking.objects.filter(season_category='all_2022_2026', is_ipl_eligible=True).order_by('rank')[:20]

    context = {
        'batters': batters,
        'bowlers': bowlers,
    }
    return render(request, 'pressure_app/ipl_eligible.html', context)

def recent_2025_2026_view(request):
    batters = BatterRanking.objects.filter(season_category='recent_2025_2026').order_by('rank')[:20]
    bowlers = BowlerRanking.objects.filter(season_category='recent_2025_2026').order_by('rank')[:20]

    context = {
        'batters': batters,
        'bowlers': bowlers,
    }
    return render(request, 'pressure_app/recent_2526.html', context)

def matches_view(request):
    query = request.GET.get('q', '').strip()
    format_filter = request.GET.get('format', 'all')
    matches = MatchSummary.objects.all()

    if format_filter == 'ipl':
        matches = matches.filter(is_ipl=True)
    elif format_filter == 't20i':
        matches = matches.filter(is_ipl=False)
    elif format_filter == 'knockout':
        matches = matches.filter(knock_out=True)

    if query:
        matches = matches.filter(Q(home_team__icontains=query) | Q(away_team__icontains=query) | Q(comp_name__icontains=query))

    matches = matches.order_by('-match_date')[:100]

    context = {
        'matches': matches,
        'query': query,
        'format': format_filter,
    }
    return render(request, 'pressure_app/matches.html', context)

def methodology_view(request):
    return render(request, 'pressure_app/methodology.html')

def strategy_view(request):
    # Load Top 20 Batters & Bowlers for Rajasthan Royals auction strategy
    bat_csv_path = os.path.join(settings.BASE_DIR, 'rr_auction_top_20_batters.csv')
    bowl_csv_path = os.path.join(settings.BASE_DIR, 'rr_auction_top_20_bowlers.csv')
    
    if not os.path.exists(bat_csv_path):
        bat_csv_path = os.path.join(settings.BASE_DIR.parent, 'rr_auction_top_20_batters.csv')
    if not os.path.exists(bowl_csv_path):
        bowl_csv_path = os.path.join(settings.BASE_DIR.parent, 'rr_auction_top_20_bowlers.csv')

    auction_batters = []
    if os.path.exists(bat_csv_path):
        df_bat = pd.read_csv(bat_csv_path)
        auction_batters = df_bat.to_dict('records')

    auction_bowlers = []
    if os.path.exists(bowl_csv_path):
        df_bowl = pd.read_csv(bowl_csv_path)
        auction_bowlers = df_bowl.to_dict('records')

    context = {
        'auction_batters': auction_batters,
        'auction_bowlers': auction_bowlers,
    }
    return render(request, 'pressure_app/strategy.html', context)

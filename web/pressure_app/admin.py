from django.contrib import admin
from .models import BatterRanking, BowlerRanking, MatchSummary


@admin.register(BatterRanking)
class BatterRankingAdmin(admin.ModelAdmin):
    list_display = ('rank', 'striker_name', 'season_category', 'is_ipl_eligible',
                    'balls_press', 'runs_press', 'sr_press', 'avg_press', 'pri_bat_score')
    list_filter = ('season_category', 'is_ipl_eligible')
    search_fields = ('striker_name',)
    ordering = ('season_category', 'rank')
    list_per_page = 50


@admin.register(BowlerRanking)
class BowlerRankingAdmin(admin.ModelAdmin):
    list_display = ('rank', 'bowler_name', 'season_category', 'is_ipl_eligible',
                    'balls_press', 'wickets_press', 'econ_press', 'sr_press', 'pri_bowl_score')
    list_filter = ('season_category', 'is_ipl_eligible')
    search_fields = ('bowler_name',)
    ordering = ('season_category', 'rank')
    list_per_page = 50


@admin.register(MatchSummary)
class MatchSummaryAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'comp_name', 'match_date', 'home_team', 'away_team',
                    'stage', 'is_ipl', 'knock_out', 'result')
    list_filter = ('is_ipl', 'knock_out', 'comp_name')
    search_fields = ('home_team', 'away_team', 'comp_name', 'result')
    ordering = ('-match_date',)
    list_per_page = 100

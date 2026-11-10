from django.db import models

class BatterRanking(models.Model):
    striker_id = models.IntegerField()
    striker_name = models.CharField(max_length=150)
    season_category = models.CharField(max_length=50, default='all_2022_2026') # 'all_2022_2026' or 'recent_2025_2026'
    is_ipl_eligible = models.BooleanField(default=True)
    rank = models.IntegerField()
    balls_press = models.IntegerField()
    runs_press = models.IntegerField()
    sr_press = models.FloatField()
    avg_press = models.FloatField()
    delta_sr = models.FloatField()
    boundary_pct_press = models.FloatField()
    dot_pct_press = models.FloatField(default=0.0)
    rsaa_bat_per_100 = models.FloatField(default=0.0)
    impact_rate = models.FloatField(default=0.0)
    pri_bat_score = models.FloatField()

    class Meta:
        db_table = 'batter_rankings'
        ordering = ['season_category', '-is_ipl_eligible', 'rank']

    def __str__(self):
        return f"#{self.rank} {self.striker_name} ({self.season_category})"


class BowlerRanking(models.Model):
    bowler_id = models.IntegerField()
    bowler_name = models.CharField(max_length=150)
    season_category = models.CharField(max_length=50, default='all_2022_2026') # 'all_2022_2026' or 'recent_2025_2026'
    is_ipl_eligible = models.BooleanField(default=True)
    rank = models.IntegerField()
    balls_press = models.IntegerField()
    wickets_press = models.IntegerField()
    econ_press = models.FloatField()
    sr_press = models.FloatField()
    dot_pct_press = models.FloatField(default=0.0)
    boundary_pct_press = models.FloatField(default=0.0)
    runs_saved_per_6 = models.FloatField(default=0.0)
    impact_rate = models.FloatField(default=0.0)
    pri_bowl_score = models.FloatField()

    class Meta:
        db_table = 'bowler_rankings'
        ordering = ['season_category', '-is_ipl_eligible', 'rank']

    def __str__(self):
        return f"#{self.rank} {self.bowler_name} ({self.season_category})"


class MatchSummary(models.Model):
    match_id = models.IntegerField(primary_key=True)
    comp_id = models.IntegerField()
    comp_name = models.CharField(max_length=200)
    match_date = models.CharField(max_length=50)
    stage = models.CharField(max_length=100)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    result = models.CharField(max_length=250)
    knock_out = models.BooleanField(default=False)
    is_ipl = models.BooleanField(default=False)

    class Meta:
        db_table = 'matches_summary'
        ordering = ['-match_date']

    def __str__(self):
        return f"{self.match_id}: {self.home_team} vs {self.away_team} ({self.comp_name})"

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('batters/', views.batters_view, name='batters'),
    path('bowlers/', views.bowlers_view, name='bowlers'),
    path('ipl-eligible/', views.ipl_eligible_view, name='ipl_eligible'),
    path('recent-2025-2026/', views.recent_2025_2026_view, name='recent_2025_2026'),
    path('matches/', views.matches_view, name='matches'),
    path('methodology/', views.methodology_view, name='methodology'),
]


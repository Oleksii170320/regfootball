from django.urls import path

from . import views


app_name = 'footballs'
urlpatterns = [
    path('', views.index, name='index'),
    path('teams/', views.teams, name='teams'),
    path('teams/<slug:team_slug>/', views.team, name='team'),
    path('new_team/', views.new_team, name='new_team'),
    path('edit_team/<slug:team_slug>/', views.edit_team, name='edit_team'),
    path('tournaments_season/', views.tournaments_season, name='tournaments_season'),
    path('tournaments/<slug:region_slug>/<slug:tournament_slug>/<slug:season_year>/', views.tournament, name='tournament'),
    path('tournaments1/', views.tournament1, name='tournament1'),
    path('tournaments_list/', views.tournaments_list, name='tournaments_list'),
    path('tournament_info/<slug:tournament_slug>/', views.tournament_info, name='tournament_info'),
    path('new_tournament/', views.new_tournament, name='new_tournament'),
    path('edit_tournament/<slug:tournament_slug>/', views.edit_tournament, name='edit_tournament'),
    path('matches/', views.matches, name='matches'),
    path('matches_test/', views.matches_test, name='matches_test'),
    path('matches_test1/', views.matches_test1, name='matches_test1'),
    path('matches/<int:match_id>/', views.match, name='match'),
    path('new_match/', views.new_match, name='new_match'),
    path('edit_match/<int:match_id>/', views.edit_match, name='edit_match'),
    # # path('type_of_sports/', views.type_of_sports, name='type_of_sports'),
    # # path('new_type/', views.new_type, name='new_type'),
    # path('seasons/', views.seasons, name='seasons'),
]

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    fields = ['team',
              'team_slug',
              'team_full_name',
              'region',
              'town',
              'address',
              'link',
              'description',
              'logotype',
              'born',
              'stadium',
              ]
    prepopulated_fields = {"team_slug": ('team', )}
    list_per_page = 10
    save_on_top = True


@admin.register(Tournaments)
class TournamentsAdmin(admin.ModelAdmin):
    fields = ['name', 'tournament_slug', 'full_name', 'region', 'description', 'link', 'logotype']
    # exclude = ['association_full_name']
    # readonly_fields = ['slug']
    prepopulated_fields = {"tournament_slug": ('name', )}
    list_per_page = 20


@admin.register(TournamentTables)
class TournamentTablesAdmin(admin.ModelAdmin):
    fields = ['region', 'tournament', 'season', 'team', ]
    list_per_page = 10
    save_on_top = True


@admin.register(Matches)
class MatchesAdmin(admin.ModelAdmin):
    fields = ('tournament', 'match_date', 'round',
              ('host_team', 'host_team_goals'),
              ('visiting_team', 'visiting_team_goals'),
              'status')
    # readonly_fields = []
    # list_display = ['tournament', 'match_date']
    # list_editable = ['host_team_goals', 'visiting_team_goals']
    # ordering = ['tournament', 'match_date']
    list_per_page = 30
    # search_fields = ['tournament']


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    fields = ['name', 'region_slug']
    prepopulated_fields = {"region_slug": ('name', )}
    list_per_page = 30


@admin.register(Rounds)
class RoundsAdmin(admin.ModelAdmin):
    fields = ['round']
    list_per_page = 30

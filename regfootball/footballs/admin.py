from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


@admin.register(Associations)
class AssociationsAdmin(admin.ModelAdmin):
    fields = ['association', 'association_slug', 'association_full_name', 'region_id', 'district', 'county', 'description', 'emblem']
    # exclude = ['association_full_name']
    # readonly_fields = ['slug']
    prepopulated_fields = {"association_slug": ('association',)}
    list_per_page = 20


@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    fields = ['team',
              'team_slug',
              'team_full_name',
              'region_id',
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
    fields = ['name', 'tournament_slug', 'full_name', 'association_id', 'description', 'link', 'logotype']
    # exclude = ['association_full_name']
    # readonly_fields = ['slug']
    prepopulated_fields = {"tournament_slug": ('name', )}
    list_per_page = 20


@admin.register(TournamentTables)
class TournamentTablesAdmin(admin.ModelAdmin):
    fields = ['region_id', 'tournament_id', 'season', 'team_id', ]
    list_per_page = 10
    save_on_top = True


@admin.register(Matches)
class MatchesAdmin(admin.ModelAdmin):
    # fields = ['tournament_id', 'match_date', 'round_id', 'match_home', 'host_team_goals', 'visiting_team_goals', 'match_guests']
    # readonly_fields = []
    # list_display = ['tournament_id', 'match_date']
    # list_editable = ['host_team_goals', 'visiting_team_goals']
    # ordering = ['tournament_id', 'match_date']
    list_per_page = 30
    # search_fields = ['tournament_id']


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    fields = ['name', 'region_slug']
    prepopulated_fields = {"region_slug": ('name', )}
    list_per_page = 30

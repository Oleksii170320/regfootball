from django.contrib import admin, messages
from django.utils.safestring import mark_safe


from .models import *


@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    list_display = ['id', 'team_logo', 'name', 'born', 'region']   # Поля таблиці, які видно відображаются в назві об'єкта
    list_display_links = ['id', 'name']                           # Поля таблиці, які видно відкивають об'єкти для редагування
    ordering = ['name']                                           # Поля таблиці, по якім відбувається сортування
    list_editable = ('born', )                                    # Поля, які можна редагувати
    list_per_page = 10                                            # Кількість видимих об'єктів на одній сторінці
    search_fields = ['name']                                      # Поля, по якім буде відбуватися пошук
    list_filter = ['name', 'region']                              # Поля по яких відбуваэться фільтрація
    fields = ['name',                                             # Поля, які видні в формі
              'team_slug',
              'full_name',
              'region',
              'town',
              'address',
              'link',
              'description',
              ('team_logo', 'logotype'),
              'born',
              'stadium',
              ]
    readonly_fields = ['team_logo']
    prepopulated_fields = {"team_slug": ('name', )}
    list_per_page = 10
    save_on_top = True

    @admin.display(description='Логотип команди')
    def team_logo(self, team: Teams):
        if team.logotype.url:
            return mark_safe(f"<img src='{team.logotype.url}' width=40>")
        return "Без логотипа"


@admin.register(Tournaments)
class TournamentsAdmin(admin.ModelAdmin):
    list_display = ['tournament_logo', 'name', 'region']
    list_display_links = ['name']
    readonly_fields = ['tournament_logo']
    fields = ['name',
              'tournament_slug',
              'full_name',
              'region',
              'description',
              'link',
              ('tournament_logo', 'logotype')
    ]
    # exclude = ['association_full_name']
    # readonly_fields = ['slug']
    prepopulated_fields = {"tournament_slug": ('name', )}
    list_per_page = 20

    @admin.display(description='Логотип турніру')
    def tournament_logo(self, tournament: Tournaments):
        if tournament.logotype.url:
            return mark_safe(f"<img src='{tournament.logotype.url}' width=40>")
        return "Без логотипа"


@admin.register(Standings)
class TournamentTablesAdmin(admin.ModelAdmin):
    list_display = ['season', 'tournament_logo', 'tournament']
    list_display_links = ['tournament']
    readonly_fields = ['tournament_logo']
    fields = ['region', 'tournament', 'season', 'team', 'print_standing', 'tournament_logo' ]
    filter_horizontal = ['team']
    list_per_page = 10
    save_on_top = True

    @admin.display(description='Логотип турніру')
    def tournament_logo(self, standings: Standings):
        if standings.tournament.logotype.url:
            return mark_safe(f"<img src='{standings.tournament.logotype.url}' width=40>")
        return "Без логотипа"


@admin.register(Matches)
class MatchesAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'match_event',
                    'team1', 'goals_team1',
                    'goals_team2', 'team2',
                    'status', 'team_1']
    list_display_links = ['tournament']
    list_editable = ('goals_team1', 'goals_team2', 'status', )  # Поля, які можна редагувати
    list_per_page = 14
    actions = ['set_none_status', 'set_status']                                     # Сортування
    # search_fields = ['tournament']
    fields = ('tournament', 'match_event', 'round',
              ('team1', 'goals_team1'),
              ('team2', 'goals_team2'),
              'status')
    # readonly_fields = []
    ordering = ['-match_event', 'tournament']

    @admin.action(description='Змінити статус на "Не зіграні"')
    def set_none_status(self, request, queryset):
        count = queryset.update(status=Matches.STATUS_MATCH.not_played)
        self.message_user(request, f'Не зіграно {count} матчів!', messages.WARNING)

    @admin.action(description='Змінити статус матчів на "Зіграні"')
    def set_status(self, request, queryset):
        count = queryset.update(status=Matches.STATUS_MATCH.played)
        self.message_user(request, f'Зіграно {count} матчів!')

    @admin.display(description='Команда 1')
    def team_1(self, match: Matches):
        return mark_safe(match.tournament.team)


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    fields = ['name', 'region_slug']
    prepopulated_fields = {"region_slug": ('name', )}
    list_per_page = 30


@admin.register(Rounds)
class RoundsAdmin(admin.ModelAdmin):
    list_display = ['round', 'into_table']
    fields = ['round', 'into_table']
    list_per_page = 30

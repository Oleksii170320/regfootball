from django.db.models import Q, F, Value, Sum, Subquery, OuterRef, Count
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import *
from .models import *

district_bd = [
    {'id': 1, 'name': "Шосткинський"},
    {'id': 2, 'name': "Конотопський"},
    {'id': 3, 'name': "Роменський"},
    {'id': 4, 'name': "Сумський"},
    {'id': 5, 'name': "Охтирський"},
]


def index(request):
    context = {
        'title': "Головна сторірка",
    }
    return render(request, 'footballs/index.html', context)


def teams(request):
    teams_list = Teams.objects.order_by('name')
    context = {
        'title': "Команди",
        'teams': teams_list,
    }
    return render(request, 'footballs/teams.html', context)


def team(request, team_slug):
    team = get_object_or_404(Teams, team_slug=team_slug)

    matches = Matches.objects.values(
        'id',
        'tournament__tournament__name',
        'tournament__tournament__id',
        'round__round',
        'round__id',
        'match_date',
        'match_time',
        'host_team__name',
        'host_team__team_slug',
        'host_team__id',
        'host_team__logotype',
        'host_goals',
        'visiting_goals',
        'visiting_team__name',
        'visiting_team__team_slug',
        'visiting_team__id',
        'visiting_team__logotype',
        'status'
    ).filter(Q(host_team__team_slug=team_slug) | Q(visiting_team__team_slug=team_slug)).order_by('-match_date', 'match_time')

    tournaments_name = set()   # Визначає всі унікальні назви турніри
    for i in matches:
        tournaments_name.add(i['tournament__tournament__name'])

    rounds = set()             # Визначає всі унікальні тури турніру
    for i in matches:
        rounds.add(i['round__round'])

    context = {
        'title': team.name,
        'team': team,
        'matches': matches,
        # Параметри, для побудови в шаблоні інформації "календар матчів":
        'tournaments_name': sorted(tournaments_name),  # сортування турнірів в порядку статусу;
        'rounds': sorted(rounds),                      # сортування раундів турніру в порядку зростання;
        'button': False,                               # Параметр, що відтворює кнопку "Редагувати матч" в кожному записі матчів;
        'round_title': False,                          # Параметр, що відтворює "Назви туру" над записами всіх матчів даного туру;
        'round_match': True,                           # Параметр, що відтворює "Назви туру" в кожному записі матчів;
        'league_title': False,                          # Параметр, що відтворює "Назву турніру" над всіма матчами даного турніру;
        'league_match': True,                         # Параметр, що вказує видимість "Назви турніру" в кожному записі матчів.
    }
    return render(request, 'footballs/team.html', context)


def uploaded_team_logo(f):
    with open(f"media/{f.name}", " wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def new_team(request):
    if request.method != 'POST':
        form = TeamsForm()
    else:
        form = TeamsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('footballs:teams')
    context = {
        'title': "Додати нову команду",
        'form': form,
    }
    return render(request, 'footballs/new_team.html', context)


def edit_team(request, team_slug):
    team = Standings.objects.get(team_slug=team_slug)
    team_name = team.name
    # if team.owner != request.user:
    #     raise Http404

    if request.method != 'POST':
        form = TeamsForm(instance=team)
    else:
        form = TeamsForm(instance=team, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('footballs:team', team_slug=team_slug)
    context = {
        'team': team,
        'team': team_name,
        'form': form,
    }
    return render(request, 'footballs/edit_team.html', context)


def tournaments_season(request):
    tournaments = Standings.objects.select_related(
        'tournament',
        'region'
    )

    context = {
        'title': "Турніри",
        'tournaments': tournaments,
    }
    return render(request, 'footballs/tournaments_season.html', context)


def tournament(request, region_slug, tournament_slug, season_year):
    """Інформація для головної сторінки Турніру (турнірна таблиця та календар матчів)"""

    """Запит для формування даних всіх матчів турніру даного розіграшу"""
    matches = Matches.objects.values(
        'id',
        'tournament__tournament__name',
        'tournament__tournament__id',
        'round__round',
        'round__id',
        'match_date',
        'match_time',
        'host_team__name',
        'host_team__team_slug',
        'host_team__id',
        'host_team__logotype',
        'host_goals',
        'visiting_goals',
        'visiting_team__name',
        'visiting_team__team_slug',
        'visiting_team__id',
        'visiting_team__logotype',
        'status'
    ).filter(tournament__tournament__tournament_slug=tournament_slug).order_by('-match_date', 'match_time')

    tournaments_name = set()      # Визначає всі унікальні назви турніри
    tournaments_title = ''
    for i in matches:
        tournaments_name.add(i['tournament__tournament__name'])
        tournaments_title = i['tournament__tournament__name']

    rounds = set()                # Визначає всі унікальні тури турніру
    for i in matches:
        rounds.add(i['round__round'])

    """Запит для формування даних для турнірної таблиці"""
    tournaments = Standings.objects.filter(
        tournament__tournament_slug=tournament_slug,
        season=season_year,
        region__region_slug=region_slug
    ).values(
        'tournament__logotype',          # лого турніру
        'tournament__full_name',         # повна назва турніру
        'season',                        # рік проведення турніру
        'team__logotype',                # лого команди-учасниці
        'team__team_slug',               # slug команди-учасниці
        'team__name',                    # коротка назва команди-учасниці
        'team'
    # ).annotate(
    #     count_wins=Value(                # кількість перемог в даному турнірі
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & ((Q(host_goals__gt=F('visiting_goals')) & Q(host_team=F('tournament__team')))
    #             | (Q(host_goals__lt=F('visiting_goals')) & Q(visiting_team=F('tournament__team'))))
    #         ).count()
    #     ),
    #
    #     count_draw=Value(                # кількість нічийних матчів в даному турнірі
    #     matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & ((Q(host_goals=F('visiting_goals')) & Q(host_team=F('tournament__team')))
    #             | (Q(host_goals=F('visiting_goals')) & Q(visiting_team=F('tournament__team'))))
    #         ).count()
    #     ),
    #
    #     count_defeat=Value(          # кількість позарок в даному турнірі
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & ((Q(host_goals__lt=F('visiting_goals')) & Q(host_team=F('tournament__team')))
    #             | (Q(host_goals__gt=F('visiting_goals')) & Q(visiting_team=F('tournament__team'))))
    #         ).count()
    #     ),
    #     count_matches=F('count_wins') + F('count_draw') + F('count_defeat'), # кількість зіграних матчів в даному турнірі
    #     goals_scored=Value(                                                  # кількість забитих голів в даному турнірі
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & Q(host_team=F('tournament__team'))
    #         ).aggregate(s=Sum('host_goals')).get('s')
    #     ) + Value(
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & Q(visiting_team=F('tournament__team'))
    #         ).aggregate(s=Sum('visiting_goals')).get('s')
    #     ),
    #     goals_conceded=Value(         # кількість пропущених голів в даному турнірі
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & Q(host_team=F('tournament__team'))
    #         ).aggregate(s=Sum('visiting_goals')).get('s')
    #     ) + Value(
    #         matches.filter(
    #             Q(status__in=('played', 'tech_defeat'))
    #             & Q(visiting_team=F('tournament__team'))
    #         ).aggregate(s=Sum('host_goals')).get('s')
    #     ),
    #     goals_difference=F('goals_scored') - F('goals_conceded'),  # різниця голів в даному турнірі
    #     points=F('count_wins') * 3 + F('count_draw') * 1,          # залікові бали в даному турнірі
    )

    standings = []
    for i in tournaments:
        standings.append(i)

    wins = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & ((Q(matches__host_goals__gt=F('matches__visiting_goals')) & Q(matches__host_team=F('team')))
        | (Q(matches__host_goals__lt=F('matches__visiting_goals')) & Q(matches__visiting_team=F('team')))
    )).values('team').annotate(count_wins=Count('id'))

    draws = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & ((Q(matches__host_goals=F('matches__visiting_goals')) & Q(matches__host_team=F('team')))
        | (Q(matches__host_goals=F('matches__visiting_goals')) & Q(matches__visiting_team=F('team')))
    )).values('team').annotate(count_draw=Count('id'))

    defeats = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & ((Q(matches__host_goals__lt=F('matches__visiting_goals')) & Q(matches__host_team=F('team')))
        | (Q(matches__host_goals__gt=F('matches__visiting_goals')) & Q(matches__visiting_team=F('team')))
    )).values('team').annotate(count_draw=Count('id'))

    home_scored_goals = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & Q(matches__host_team=F('team'))
    ).values('team').annotate(host_goals=Sum('matches__host_goals'))

    visit_scored_goals = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & Q(matches__visiting_team=F('team'))
    ).values('team').annotate(visiting_goals=Sum('matches__visiting_goals'))

    home_conceded_goals = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & Q(matches__visiting_team=F('team'))
    ).values('team').annotate(host_goals=Sum('matches__host_goals'))

    visit_conceded_goals = Standings.objects.filter(
        Q(tournament__tournament_slug=tournament_slug)
        & Q(season=season_year)
        & Q(region__region_slug=region_slug)
        & Q(matches__status__in=('played', 'tech_defeat'))
        & Q(matches__host_team=F('team'))
    ).values('team').annotate(visiting_goals=Sum('matches__visiting_goals'))

    for team in standings:
        team['count_wins'] = 0
        team['count_draw'] = 0
        team['count_defeat'] = 0
        team['count_matches'] = 0
        team['points'] = 0
        team['goals_scored_host'] = 0
        team['goals_scored_visit'] = 0
        team['goals_scored'] = 0
        team['goals_conceded_host'] = 0
        team['goals_conceded_visit'] = 0
        team['goals_conceded'] = 0
        team['goals_difference'] = 0

        for win in wins:
            if team['team'] == win['team']:
                if win['count_wins']:
                    team['count_wins'] = win['count_wins']
        for draw in draws:
            if team['team'] == draw['team']:
                if draw['count_draw']:
                    team['count_draw'] = draw['count_draw']
        for defeat in defeats:
            if team['team'] == defeat['team']:
                if defeat['count_draw']:
                    team['count_defeat'] = defeat['count_draw']

        team['count_matches'] = team['count_wins'] + team['count_draw'] + team['count_defeat']
        team['points'] = team['count_wins'] * 3 + team['count_draw'] * 1

        for scored_goal in home_scored_goals:
            if team['team'] == scored_goal['team']:
                if scored_goal['host_goals']:
                    team['goals_scored_host'] = scored_goal['host_goals']
        for scored_goal in visit_scored_goals:
            if team['team'] == scored_goal['team']:
                if scored_goal['visiting_goals']:
                    team['goals_scored_visit'] = scored_goal['visiting_goals']

        for conceded_goal in home_conceded_goals:
            if team['team'] == conceded_goal['team']:
                if conceded_goal['host_goals']:
                    team['goals_conceded_host'] = conceded_goal['host_goals']

        for conceded_goal in visit_conceded_goals:
            if team['team'] == conceded_goal['team']:
                if conceded_goal['visiting_goals']:
                    team['goals_conceded_visit'] = conceded_goal['visiting_goals']

        team['goals_scored'] = team['goals_scored_host'] + team['goals_scored_visit']
        team['goals_conceded'] = team['goals_conceded_host'] + team['goals_conceded_visit']
        team['goals_difference'] = team['goals_scored'] - team['goals_conceded']

    context = {
        'title': tournaments_title,                    # назва турніру для закладки браузера
        'tournaments': standings,                    # Дані для формування турнірної таблиці
        'matches': matches,                            # Дані для формування календаря матчів

        # Параметри, для побудови в шаблоні інформації "календар матчів":
        'tournaments_name': sorted(tournaments_name),  # сортування турнірів в порядку статусу;
        'rounds': sorted(rounds),                      # сортування раундів турніру в порядку зростання;
        'button': False,                               # Параметр, що відтворює кнопку "Редагувати матч" в кожному записі матчів;
        'round_title': True,                           # Параметр, що відтворює "Назви туру" над записами всіх матчів даного туру;
        'round_match': False,                          # Параметр, що відтворює "Назви туру" в кожному записі матчів;
        'league_title': False,                         # Параметр, що відтворює "Назву турніру" над всіма матчами даного турніру;
        'league_match': False,                         # Параметр, що вказує видимість "Назви турніру" в кожному записі матчів.
    }
    return render(request, 'footballs/tournament.html', context)


def tournaments_list(request):
    tournaments_list = Tournaments.objects.order_by('date_create')

    context = {
        'title': "Турніри",
        'tournaments': tournaments_list,
    }
    return render(request, 'footballs/tournaments_list.html', context)


def tournament_info(request, tournament_slug):
    tournament = Tournaments.objects.get(tournament_slug=tournament_slug)

    context = {
        'title': tournament.name,
        'tournament': tournament,
    }
    return render(request, 'footballs/tournament_info.html', context)


def new_tournament(request):
    if request.method != 'POST':
        form = TournamentsForm()
    else:
        form = TournamentsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('footballs:tournaments_list')
    context = {
        'title': "Додати турнір",
        'form': form,
    }
    return render(request, 'footballs/new_tournament.html', context)


def edit_tournament(request, tournament_slug):
    tournament = Tournaments.objects.get(tournament_slug=tournament_slug)
    name = tournament.name
    # if team.owner != request.user:
    #     raise Http404

    if request.method != 'POST':
        form = TournamentsForm(instance=tournament)
    else:
        form = TournamentsForm(instance=tournament, data=(request.POST, request.FILES))
        if form.is_valid():
            form.save()
            return redirect('footballs:tournament', tournament_slug=tournament_slug)
    context = {
        'tournament': tournament,
        'name': name,
        'form': form,
    }
    return render(request, 'footballs/edit_tournament.html', context)


def matches(request):
    """Інформація для сторінки 'всі матчі сезону' """

    matches = Matches.objects.values(
        'id',
        'tournament__tournament__name',
        'tournament__tournament__id',
        'round__round',
        'round__id',
        'match_date',
        'match_time',
        'host_team__name',
        'host_team__team_slug',
        'host_team__id',
        'host_team__logotype',
        'host_goals',
        'visiting_goals',
        'visiting_team__name',
        'visiting_team__team_slug',
        'visiting_team__id',
        'visiting_team__logotype',
        'status'
    ).order_by('-match_date', 'match_time')
    tournaments_name = set()   # Визначає всі унікальні назви турніри
    for i in matches:
        tournaments_name.add(i['tournament__tournament__name'])

    rounds = set()             # Визначає всі унікальні тури турніру
    for i in matches:
        rounds.add(i['round__round'])

    context = {
        'title': "Матчі сезону",
        'matches': matches,
        # Параметри, для побудови в шаблоні інформації "календар матчів":
        'tournaments_name': sorted(tournaments_name),  # сортування турнірів в порядку статусу;
        'rounds': sorted(rounds),                      # сортування раундів турніру в порядку зростання;
        'button': False,                               # Параметр, що відтворює кнопку "Редагувати матч" в кожному записі матчів;
        'round_title': False,                          # Параметр, що відтворює "Назви туру" над записами всіх матчів даного туру;
        'round_match': True,                           # Параметр, що відтворює "Назви туру" в кожному записі матчів;
        'league_title': True,                          # Параметр, що відтворює "Назву турніру" над всіма матчами даного турніру;
        'league_match': False,                         # Параметр, що вказує видимість "Назви турніру" в кожному записі матчів.
    }
    return render(request, 'footballs/matches.html', context)


def matches_test(request):
    """Інформація для сторінки 'всі матчі сезону' """
    matches = Matches.objects.select_related('tournament',
                                             'host_team',
                                             'visiting_team',
                                             'tournament__region',
                                             'round',
                                             'tournament__tournament'
    ).order_by('-match_date', 'match_time')

    tournaments_name = set()   # Визначає всі унікальні назви турніри
    for i in matches:
        tournaments_name.add(i.tournament.tournament.name)

    rounds = set()
    for i in matches:
        rounds.add(i.round.round)

    context = {
        'title': "Матчі сезону",
        'matches': matches,
        # Параметри, для побудови в шаблоні інформації "календар матчів":
        'tournaments_name': sorted(tournaments_name),  # сортування турнірів в порядку статусу;
        'rounds': sorted(rounds),                      # сортування раундів турніру в порядку зростання;
        'button': False,                               # Параметр, що відтворює кнопку "Редагувати матч" в кожному записі матчів;
        'round_title': False,                          # Параметр, що відтворює "Назви туру" над записами всіх матчів даного туру;
        'round_match': True,                           # Параметр, що відтворює "Назви туру" в кожному записі матчів;
        'league_title': True,                          # Параметр, що відтворює "Назву турніру" над всіма матчами даного турніру;
        'league_match': False,                         # Параметр, що вказує видимість "Назви турніру" в кожному записі матчів.
    }
    return render(request, 'footballs/matches_test.html', context)


def match(request, match_id):
    match = Matches.objects.get(id=match_id)

    context = {
        'title': match,
        'match': match,
    }
    return render(request, 'footballs/match.html', context)


def new_match(request):
    if request.method != 'POST':
        form = MatchesForm()
    else:
        form = MatchesForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('footballs:matches')
    context = {
        'title': "Додати матч",
        'form': form,
    }
    return render(request, 'footballs/new_match.html', context)


def edit_match(request, match_id):
    match = Matches.objects.get(id=match_id)

    if request.method != 'POST':
        form = MatchesForm(instance=match)
    else:
        form = MatchesForm(instance=match, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('footballs:match', match_id=match.id)
    context = {
        'match': match,
        'form': form,
    }

    return render(request, 'footballs/edit_match.html', context)

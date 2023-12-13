from django.db.models import Q
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
    teams_list = Teams.objects.order_by('date_create')
    context = {
        'title': "Команди",
        'teams': teams_list,
    }
    return render(request, 'footballs/teams.html', context)


def team(request, team_slug):
    team = get_object_or_404(Teams, team_slug=team_slug)
    # team_id = team.id
    # matches = Matches.objects.filter(Q(match_team_home_id=team_id) | Q(visiting_team_id=team_id)).order_by(
    #     '-match_date')
    #
    # tournams = set({})
    # for i in matches:
    #     tournams.add(i.tournament_id)
    #
    # tours = set({})  # Визначає всі тури сесону
    # for i in matches:
    #     tours.add(i.round_id)

    context = {
        'title': team.team,
        'team': team,
        # 'matches': matches,
        # 'tours': tours,
        # 'tournams': tournams,
        # 'button': False,  # Видимість кнопки "Редагувати матч"
        # 'tour_title': False,  # Видимість "Назви туру" в заголовку
        # 'tour_match': True,  # Видимість "Назви туру" в матчі
        # 'league_title': True,  # Видимість "Назви турніру"
        # 'league_match': False,  # Видимість "Назви турніру" в матчі
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
    team = TournamentTables.objects.get(team_slug=team_slug)
    team_name = team.team
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
        'team ': team_name,
        'form': form,
    }
    return render(request, 'footballs/edit_team.html', context)


def tournaments_season(request):
    tournaments_list = TournamentTables.objects.all()

    context = {
        'title': "Турніри",
        'tournaments': tournaments_list,
    }
    return render(request, 'footballs/tournaments_season.html', context)


def tournament(request, region_id, tournament_slug, season_year):
    tournament = Tournaments.objects.get(tournament_slug=tournament_slug)  # визначення турніру
    tournament_id = tournament.id
    table = TournamentTables.objects.get(
        tournament=tournament.id,
        season=season_year
    ).team_id.order_by('team').all()  # визначення команд данного турніру

    matches = Matches.objects.filter(tournament_id=tournament_id).order_by('-match_date',
                                                                           'match_time').all()  # визначення всіх матчів даного турніру
    tournament_unique = set()
    for i in matches:
        tournament_unique.add(i.tournament_id)

    print_table = False  # Признак, чи потрібно виводити турнірну таблицю

    tours_unique = set()  # Визначає всі тури сезону
    for i in matches:
        tours_unique.add(i.round_id)
        if i.round_id.id < 7:
            print_table = True
        else:
            print_table = False

    rez_list = list()  # Словник таблиці результатів
    for team in table:  # кількості зіграних матчів в турнірі певною командою
        team_result = matches.filter(
            Q(tournament_id=tournament_id)
            & (Q(host_team_id=team.id) | Q(visiting_team_id=team.id))
            & Q(match_status__in=('played', 'tech_defeat')))

        # кількості матчів в турнірі однієї команди (дома - на виїзді)
        match_home = matches.filter(
            Q(tournament_id=tournament_id) & Q(host_team_id=team.id) & Q(
                match_status__in=('played', 'tech_defeat'))).all()
        match_guests = matches.filter(
            Q(tournament_id=tournament_id) & Q(visiting_team_id=team.id) & Q(
                match_status__in=('played', 'tech_defeat'))).all()

        # Перемінні для підрахунку перемог-нічиїх-поразок в матчах турніру
        count_v_h, count_n_h, count_p_h = 0, 0, 0
        count_v_g, count_n_g, count_p_g = 0, 0, 0

        for i in match_home:  # Цикли домашніх матчів
            if i.host_team_goals > i.visiting_team_goals:  # Виграші
                count_v_h = count_v_h + 1
            elif i.host_team_goals == i.visiting_team_goals:  # Нічиї
                count_n_h = count_n_h + 1
            elif i.host_team_goals < i.visiting_team_goals:  # Поразки
                count_p_h = count_p_h + 1

        for j in match_guests:  # Цикли матчів на виїзді
            if j.host_team_goals < j.visiting_team_goals:  # Виграші
                count_v_g = count_v_g + 1
            elif j.host_team_goals == j.visiting_team_goals:  # Нічиї
                count_n_g = count_n_g + 1
            elif j.host_team_goals > j.visiting_team_goals:  # Поразки
                count_p_g = count_p_g + 1

        match_victory = count_v_g + count_v_h
        match_nichiya = count_n_g + count_n_h
        match_losing = count_p_g + count_p_h

        points = (match_victory * 3) + (match_nichiya * 1)  # Розрахунок залікових білів

        # визначення забитих голів
        goals_home, goals_guests = 0, 0

        for i in match_home:
            goals_home = goals_home + i.host_team_goals
        for j in match_guests:
            goals_guests = goals_guests + j.visiting_team_goals

        goals_scored = goals_home + goals_guests

        # визначення пропущених голів
        goals_home, goals_guests = 0, 0

        for i in match_home:
            goals_home = goals_home + i.visiting_team_goals
        for j in match_guests:
            goals_guests = goals_guests + j.host_team_goals

        goals_missed = goals_home + goals_guests

        # визначення різниці голів
        goals = int(goals_scored) - int(goals_missed)

        rez_list.append({  # формування словника турнірної таблиці
            'team_o': points,  # Залікові бали
            'team': team,  # Назва команди
            'team_i': team_result.count(),  # Кількість зіграних матчів
            'team_v': match_victory,  # Виграші
            'team_n': match_nichiya,  # Нічиї
            'team_p': match_losing,  # Перемоги
            'team_zm': goals_scored,  # Забиті голи
            'team_pm': goals_missed,  # Пропущені голи
            'team_rm': goals,  # Різниця (Забиті-пропущені)
        },
        )

    # формування та сортування команд згідно турнірного становища
    new_max_list = list()
    for i in rez_list:
        new_max_list.append(i['team_o'])

    max_list = sorted(new_max_list)
    new_rez_list = list()

    while rez_list:
        for i in rez_list:
            if int(i['team_o']) == max(max_list):
                max_list.pop()
                new_rez_list.append(i)
                rez_list.remove(i)

    context = {
        'title': tournament.name,
        'tournament': tournament,
        'table': table,
        'tournament_unique': tournament_unique,
        'standings': new_rez_list,
        'teams': table,
        'matches': matches,
        'tours_unique': tours_unique,
        'button': False,  # Видимість кнопки "Редагувати матч"
        'tour_title': True,  # Видимість "Назви туру" в заголовку
        'tour_match': False,  # Видимість "Назви туру" в матчі
        'league_title': False,  # Видимість "Назви турніру"
        'league_match': False,  # Видимість "Назви турніру" в матчі
        'print_table': print_table
    }
    return render(request, 'footballs/tournament.html', context)


def tournaments_list(request):
    tournaments_list = Tournaments.objects.order_by('date_create')
    # table_list = TournamentTables.objects.all()

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
    matches = Matches.objects.order_by('-match_date', 'tournament_id', 'match_time')

    tournams = set({})  # Визначає всі турніри сесону
    for i in matches:
        tournams.add(i.tournament_id)

    tours = set({})  # Визначає всі тури сесону
    for i in matches:
        tours.add(i.round_id)

    context = {
        'title': "Матчі сезону",
        'tournams': tournams,
        'matches': matches,
        'tours': tours,
        'button': False,  # Видимість кнопки "Редагувати матч"
        'tour_title': False,  # Видимість "Назви туру" в заголовку
        'tour_match': True,  # Видимість "Назви туру" в матчі
        'league_title': True,  # Видимість "Назви турніру"
        'league_match': False,  # Видимість "Назви турніру" в матчі
    }
    return render(request, 'footballs/matches.html', context)


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

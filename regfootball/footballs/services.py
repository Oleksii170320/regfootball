def tournament(request, region_slug, tournament_slug, season_year):
    """Інформація для головної сторінки Турніру (турнірна таблиця та календар матчів)"""

    """Запит для формування даних всіх матчів турніру даного розіграшу"""
    matches = Matches.objects.values(
        'id',
        'tournament__tournament__name',
        'tournament__tournament__id',
        'round__round',
        'round__id',
        'match_event',
        'team1__name',
        'team1__team_slug',
        'team1__id',
        'team1__logotype',
        'goals_team1',
        'goals_team2',
        'team2__name',
        'team2__team_slug',
        'team2__id',
        'team2__logotype',
        'status'
    ).filter(tournament__tournament__tournament_slug=tournament_slug).order_by('-match_event')

    tournaments_name = set()  # Визначає всі унікальні назви турніри
    tournaments_title = ''
    for i in matches:
        tournaments_name.add(i['tournament__tournament__name'])
        tournaments_title = i['tournament__tournament__name']

    rounds = set()  # Визначає всі унікальні тури турніру
    for i in matches:
        rounds.add(i['round__round'])

    """Запит для формування даних для турнірної таблиці"""
    standings = Standings.objects.filter(
        tournament__tournament_slug=tournament_slug,
        season=season_year,
        region__region_slug=region_slug
    ).values(
        'tournament__logotype',  # лого турніру
        'tournament__full_name',  # повна назва турніру
        'season',  # рік проведення турніру
        'team__logotype',  # лого команди-учасниці
        'team__team_slug',  # slug команди-учасниці
        'team__name',  # коротка назва команди-учасниці
        'team'
    ).annotate(
        count_wins=Value(  # кількість перемог в даному турнірі
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & ((Q(goals_team1__gt=F('goals_team2')) & Q(team1=F('tournament__team')))
                   | (Q(goals_team1__lt=F('goals_team2')) & Q(team2=F('tournament__team'))))
            ).count()
        ),

        count_draws=Value(  # кількість нічийних матчів в даному турнірі
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & ((Q(goals_team1=F('goals_team2')) & Q(team1=F('tournament__team')))
                   | (Q(goals_team1=F('goals_team2')) & Q(team2=F('tournament__team'))))
            ).count()
        ),

        count_defeats=Value(  # кількість позарок в даному турнірі
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & ((Q(goals_team1__lt=F('goals_team2')) & Q(team1=F('tournament__team')))
                   | (Q(goals_team1__gt=F('goals_team2')) & Q(team2=F('tournament__team'))))
            ).count()
        ),
        count_matches=F('count_wins') + F('count_draws') + F('count_defeats'),
        # кількість зіграних матчів в даному турнірі
        goals_scored=Value(  # кількість забитих голів в даному турнірі
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & Q(team1=F('tournament__team'))
            ).aggregate(s=Sum('goals_team1')).get('s')
        ) + Value(
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & Q(team2=F('tournament__team'))
            ).aggregate(s=Sum('goals_team2')).get('s')
        ),
        goals_conceded=Value(  # кількість пропущених голів в даному турнірі
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & Q(team1=F('tournament__team'))
            ).aggregate(s=Sum('goals_team2')).get('s')
        ) + Value(
            matches.filter(
                Q(status__in=('played', 'tech_defeat'))
                & Q(team2=F('tournament__team'))
            ).aggregate(s=Sum('goals_team1')).get('s')
        ),
        goals_difference=F('goals_scored') - F('goals_conceded'),  # різниця голів в даному турнірі
        points=F('count_wins') * 3 + F('count_draws') * 1,  # залікові бали в даному турнірі
    )

    context = {
        'title': tournaments_title,  # назва турніру для закладки браузера
        'tournaments': standings,  # Дані для формування турнірної таблиці
        'matches': matches,  # Дані для формування календаря матчів

        # Параметри, для побудови в шаблоні інформації "календар матчів":
        'tournaments_name': sorted(tournaments_name),  # сортування турнірів в порядку статусу;
        'rounds': sorted(rounds),  # сортування раундів турніру в порядку зростання;
        'button': False,  # Параметр, що відтворює кнопку "Редагувати матч" в кожному записі матчів;
        'round_title': True,  # Параметр, що відтворює "Назви туру" над записами всіх матчів даного туру;
        'round_match': False,  # Параметр, що відтворює "Назви туру" в кожному записі матчів;
        'league_title': False,  # Параметр, що відтворює "Назву турніру" над всіма матчами даного турніру;
        'league_match': False,  # Параметр, що вказує видимість "Назви турніру" в кожному записі матчів.
    }
    return render(request, 'footballs/tournament2.html', context)

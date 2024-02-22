from django.db.models import Q, F, Value, Sum, Subquery, OuterRef, Count, Case, When
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from footballs.forms import *
from footballs.models import *


def matches_list():
    """Запит для формування даних всіх матчів турніру даного розіграшу"""
    return Matches.objects.values(
        'id',
        'tournament__tournament__name',
        'tournament__tournament__id',
        'tournament__tournament__logotype',
        'tournament__tournament__full_name',
        'tournament__season',
        'round__round',
        'round__id',
        'round__into_table',
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
    ).order_by('-match_event')


def matches_tests():
    """Інформація для сторінки 'всі матчі сезону' """
    return Matches.objects.select_related(
        'tournament',
        'team1',
        'team2',
        'tournament__region',
        'round',
        'tournament__tournament'
    ).order_by('-match_event')


def tournament_teams1(tournament_slug):
    """Запит для формування даних для турнірної таблиці"""
    return Teams.objects.filter(
        teams1__tournament__tournament__tournament_slug=tournament_slug
    ).values(
        'name',
        'id'
    ).annotate(
        count_wins=Sum(Case(When(
            (
                Q(id=F('teams1__team1'))
                & Q(teams1__goals_team1__gt=F('teams1__goals_team2'))
            ) | (
                Q(id=F('teams1__team2'))
                & Q(teams1__goals_team1__lt=F('teams1__goals_team2'))
            ),
            then=1),
            default=0)
        ),
        count_draws=Sum(Case(When(
            Q(teams1__goals_team1=F('teams1__goals_team2')),
            then=1),
            default=0)
        ),
        count_defeats=Sum(Case(When(
            (
                Q(id=F('teams1__team1'))
                & Q(teams1__goals_team1__lt=F('teams1__goals_team2'))
            ) | (
                Q(id=F('teams1__team2'))
                & Q(teams1__goals_team1__gt=F('teams1__goals_team2'))
            ),
            then=1),
            default=0)
        ),
        goals_scored=Sum(Case(When(
            id=F('teams1__team1'),
            then=F('teams1__goals_team1')),
            default=F('teams1__goals_team2'))
        ),
        goals_conceded=Sum(Case(When(
            id=F('teams1__team2'),
            then=F('teams1__goals_team1')),
            default=F('teams1__goals_team2') )
        )
    ).annotate(
        count_matches=F('count_wins') + F('count_draws') + F('count_defeats'),
        points=F('count_wins') * 3 + F('count_draws'),
        goals_difference=F('goals_scored') - F('goals_conceded')
    ).values(
        'name',
        'team_slug',
        'logotype',
        'count_wins',
        'count_draws',
        'count_defeats',
        'count_matches',
        'goals_scored',
        'goals_conceded',
        'goals_difference',
        'points'
    )


def tournament_teams2(tournament_slug):
    """Запит для формування даних для турнірної таблиці"""
    return Teams.objects.filter(
        teams2__tournament__tournament__tournament_slug=tournament_slug
    ).values(
        'name',
        'id'
    ).annotate(
        count_wins=Sum(Case(When(
             (
                Q(id=F('teams2__team1'))
                & Q(teams2__goals_team1__gt=F('teams2__goals_team2'))
             ) | (
                Q(id=F('teams2__team2'))
                & Q(teams2__goals_team1__lt=F('teams2__goals_team2'))
             ),
            then=1),
            default=0)
        ),
        count_draws=Sum(Case(When(
            Q(teams2__goals_team1=F('teams2__goals_team2')),
            then=1),
            default=0)
        ),
        count_defeats=Sum(Case(When(
             (
                Q(id=F('teams2__team1'))
                & Q(teams2__goals_team1__lt=F('teams2__goals_team2'))
             ) | (
                Q(id=F('teams2__team2'))
                & Q(teams2__goals_team1__gt=F('teams2__goals_team2'))
             ),
            then=1),
            default=0)
        ),
        goals_scored=Sum(Case(When(
            id=F('teams2__team1'),
            then=F('teams2__goals_team1')),
            default=F('teams2__goals_team2'))
        ),
        goals_conceded=Sum(Case(When(
            id=F('teams2__team2'),
            then=F('teams2__goals_team1')),
            default=F('teams2__goals_team2') )
        )
    ).annotate(
        count_matches=F('count_wins') + F('count_draws') + F('count_defeats'),
        points=F('count_wins') * 3 + F('count_draws'),
        goals_difference=F('goals_scored') - F('goals_conceded')
    ).values(
        'name',
        'team_slug',
        'logotype',
        'count_wins',
        'count_draws',
        'count_defeats',
        'count_matches',
        'goals_scored',
        'goals_conceded',
        'goals_difference',
        'points'
    )


def tournament_test1(tournament_slug=None, season=None, region_slug=None):
    return Teams.objects.raw(f'''
        SELECT  query.* 
                ,goals_scored - goals_conceded AS goals_difference 
                ,3*count_wins+count_draws AS points 
        FROM (
            SELECT 
                t.id        AS id, 
                t.name      AS name,
                t.logotype  AS logotype,
                t.team_slug AS team_slug,
                tr.name     AS tournament,
                ro.into_table,	
                COUNT(m.id) AS count_matches
                 ,SUM(CASE WHEN (t.id = m.team1_id AND m.goals_team1 > m.goals_team2) 
                             OR (t.id = m.team2_id AND m.goals_team1 < m.goals_team2) THEN 1 ELSE 0 END) AS count_wins
                 ,SUM(CASE WHEN m.goals_team1 = m.goals_team2 THEN 1 ELSE 0 END) AS count_draws
                 ,SUM(CASE WHEN (t.id = m.team1_id AND m.goals_team1 < m.goals_team2) 
                             OR (t.id = m.team2_id AND m.goals_team1 > m.goals_team2) THEN 1 ELSE 0 END) AS count_defeats
                  ,SUM(CASE WHEN t.id = m.team1_id THEN m.goals_team1 ELSE goals_team2 END) AS goals_scored
                  ,SUM(CASE WHEN t.id = m.team2_id THEN m.goals_team1 ELSE goals_team2 END) AS goals_conceded
            FROM footballs_teams t
            JOIN footballs_matches      m ON t.id = m.team1_id OR t.id = m.team2_id
			JOIN footballs_standings    s ON m.tournament_id = s.id
			JOIN footballs_regions      r ON s.region_id = r.id
			JOIN footballs_tournaments tr ON s.tournament_id = tr.id
			JOIN footballs_rounds      ro ON m.round_id = ro.id
            WHERE tr.tournament_slug = '{tournament_slug}'
             AND s.season = '{season}' 
             AND r.region_slug = '{region_slug}'
		     AND m.status IN ('played', 'tech_defeat')
		     AND ro.into_table != 0
          GROUP BY t.id
        ) query 
    ''')

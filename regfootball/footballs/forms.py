from django import forms

from .models import *


class TeamsForm(forms.ModelForm):
    class Meta:
        model = TournamentTables
        fields = [
            'region_id',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class TournamentsForm(forms.ModelForm):
    class Meta:
        model = Tournaments
        fields = [
            'name',
            'full_name',
            'association_id',
            'description',
            'link',
            'logotype',
        ]
        # labels = {'text': ''}
        widgets = {'tournaments_desc': forms.Textarea(attrs={'cols': 80})}


class MatchesForm(forms.ModelForm):
    class Meta:
        model = Matches
        fields = [
            'match_date',
            'match_time',
            'tournament_id',
            'host_team_id',
            'host_team_goals',
            'visiting_team_id',
            'visiting_team_goals',
            'status',
        ]

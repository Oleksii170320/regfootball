from django import forms

from .models import *


class TeamsForm(forms.ModelForm):
    class Meta:
        model = Standings
        fields = [
            'region',
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
            'match_event',
            'tournament',
            'team1',
            'goals_team1',
            'team2',
            'goals_team2',
            'status',
        ]

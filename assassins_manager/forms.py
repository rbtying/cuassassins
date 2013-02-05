from django import forms
from assassins_manager.models import *

class GameSelectForm(forms.Form):
    """ Form which includes all incomplete games """
    game = forms.ModelChoiceField(queryset=Game.objects.filter(status__lt=GameStatus.COMPLETE))

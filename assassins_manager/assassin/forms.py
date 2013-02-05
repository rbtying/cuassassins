from django import forms
from assassins_manager.models import Assassin, Squad, Contract

class AssassinEditForm(forms.ModelForm):
    """ Form to edit assassin pictures in the details page """
    class Meta:
        model = Assassin
        fields = ('picture',)

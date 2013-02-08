from django import forms
from assassins_manager.models import *

class AddGameForm(forms.ModelForm):
    """ Form to add a game """
    class Meta:
        model=Game
        fields=('name', 'squadsize', 'disavowed_time', 'police_resurrect_time', 'code',)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
            Game.objects.get(name=name)
        except:
            return name
        raise forms.ValidationError('Game name already in use')

    def clean_code(self):
        code = self.cleaned_data.get('code')
        import re
        cleaned = re.sub(r'\W+', '', code)
        if cleaned == code and len(code) > 0 and len(code) < 10:
            return cleaned
        raise forms.ValidationError('Code should be alphanumeric characters only, between 1 and 10 characters')

class VerifyForm(forms.Form):
    """ Form to make sure admin is OK with moving forward """
    are_you_sure = forms.BooleanField()

class AddPoliceForm(forms.Form):
    """ Form to add police to a game """

    def __init__(self, *args, **kwargs):
        self.game = kwargs.pop('game', None)
        super(AddPoliceForm, self).__init__(*args, **kwargs)

        qset = Assassin.objects.filter(game=self.game).exclude(role=AssassinType.POLICE)
        
        self.fields['police'] = forms.ModelChoiceField(queryset=qset)

    def clean_police(self):
        police = self.cleaned_data.get('police')
        if police is None:
            raise forms.ValidationError('Assassin does not exist')

        if not police.squad is None:
            raise forms.ValidationError('%s is already in a squad' % police.user.username)
        
        return police

class RemovePoliceForm(forms.Form):
    """ Form to remove police to a game """

    def __init__(self, *args, **kwargs):
        self.game = kwargs.pop('game', None)
        super(RemovePoliceForm, self).__init__(*args, **kwargs)

        qset = Assassin.objects.filter(game=self.game, role=AssassinType.POLICE)
        
        self.fields['police'] = forms.ModelChoiceField(queryset=qset)

    def clean_police(self):
        police = self.cleaned_data.get('police')
        if police is None:
            raise forms.ValidationError('Assassin does not exist')

        if not police.role == AssassinType.POLICE:
            raise forms.ValidationError('Assassin is not a policeman')
        
        return police

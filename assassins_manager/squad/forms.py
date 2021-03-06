from django import forms
from assassins_manager.models import *

class AddForm(forms.ModelForm):
    """ Form to add a new squad to the game

        Takes the squad creator as a kwarg
    """
    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(AddForm, self).__init__(*args, **kwargs)
        self.game = self.assassin.game
        self.fields['code'].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
            self.game.squad_set.get(name=self.cleaned_data.get('name'))
        except Squad.DoesNotExist:
            return name
        raise forms.ValidationError('Squad name already in use')

    def clean(self):
        if not self.game.status == GameStatus.REGISTRATION:
            raise forms.ValidationError('Registration is not open at this time')
        if not self.assassin.squad is None:
            raise forms.ValidationError('You are already in a squad')
        if self.assassin.role == AssassinType.NOT_IN_GAME:
            raise forms.ValidationError('You need to join the game before you can create a sqaud')
        if not self.cleaned_data.get('public'):
            code = self.cleaned_data.get('code');
            import re
            cleaned = re.sub(r'\W+', '', code)
            if not code == cleaned or len(code) == 0:
                raise forms.ValidationError('Please enter an alphanumeric join code, or make your squad public')
            if len(code) > 10:
                raise forms.ValidationError('The squad code must be less than 10 characters long')
        return self.cleaned_data

    def save(self, commit=True):
        squad = super(AddForm, self).save(commit=False)
        squad.set_life(True, False)
        squad.kills = 0
        squad.game = self.game
        if commit:
            squad.save()
        return squad
        
    class Meta:
        model=Squad
        fields = ('name', 'public', 'code',)

class LeaveForm(forms.Form):
    """ Checks if the user really wants to leave """
    sure = forms.BooleanField(label="Are you sure you want to leave?")

    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(LeaveForm, self).__init__(*args, **kwargs)
        self.game = self.assassin.game

    def clean_sure(self):
        if not self.cleaned_data.get('sure'):
            raise forms.ValidationError('You need to check the box to leave your squad')

    def clean(self):
        if not self.game.status == GameStatus.REGISTRATION:
            raise forms.ValidationError('You can\'t leave after the game has begun')
        return self.cleaned_data

class JoinForm(forms.Form):
    """ Form to help users join squads """
    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(JoinForm, self).__init__(*args, **kwargs)
        self.game = self.assassin.game
        self.fields['squad'] = forms.ModelChoiceField(queryset=Squad.objects.filter(game=self.game))
        self.fields['code'] = forms.CharField(max_length=10, required=False)
        self.fields.keyOrder = ['squad', 'code']

    def clean(self):
        if not self.game.status == GameStatus.REGISTRATION:
            raise forms.ValidationError('Registration is not open at this time')
        if not self.assassin.squad is None:
            raise forms.ValidationError('You are already in a squad')
        if self.assassin.role == AssassinType.NOT_IN_GAME:
            raise forms.ValidationError('You need to join the game before you can create a sqaud')
        squad = self.cleaned_data.get('squad')
        if squad is None:
            raise forms.ValidationError('Please pick a squad')
        if not squad.public:
            if self.cleaned_data.get('code').strip().lower() != squad.code.lower():
                raise forms.ValidationError('Please enter the correct join code')
        return self.cleaned_data

    def clean_squad(self):
        squad = self.cleaned_data['squad']
        maxmembers = self.game.squadsize
        if squad.assassin_set.count() > self.game.squadsize:
            raise forms.ValidationError('This game only allows squads of %d or less' % self.game.squadsize)
        return squad

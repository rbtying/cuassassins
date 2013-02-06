from django import forms
from assassins_manager.models import *

class AddForm(forms.ModelForm):
    """ Form to add a new squad to the game

        Takes the squad creator as a kwarg
    """
    gamecode = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(AddForm, self).__init__(*args, **kwargs)
        self.game = self.assassin.game

    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
            self.game.squad_set.get(name=self.cleaned_data.get('name'))
        except Squad.DoesNotExist:
            return name
        raise forms.ValidationError('Squad name already in use')

    def clean_gamecode(self):
        gamecode = self.cleaned_data.get('gamecode')
        if not gamecode is None:
            if self.game.code.lower() == gamecode.strip().lower():
                return gamecode.strip().lower()
        raise forms.ValidationError('Incorrect join code')

    def clean(self):
        if not self.game.status == GameStatus.REGISTRATION:
            raise forms.ValidationError('Registration is not open at this time')
        if not self.assassin.squad is None:
            raise forms.ValidationError('You are already in a squad')
        return self.cleaned_data

    def save(self, commit=True):
        squad = super(AddForm, self).save(commit=False)
        squad.set_life(True, False)
        squad.kills = 0
        squad.game = self.game
        squad.generateCode()
        if commit:
            squad.save()
        return squad
        
    class Meta:
        model=Squad
        fields = ('gamecode', 'name', 'public', )

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
    gamecode = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(JoinForm, self).__init__(*args, **kwargs)
        self.game = self.assassin.game
        self.fields['squad'] = forms.ModelChoiceField(queryset=Squad.objects.filter(game=self.game))
        self.fields['code'] = forms.CharField(max_length=10, required=False)
        self.fields.keyOrder = ['gamecode', 'squad', 'code']

    def clean(self):
        if not self.game.status == GameStatus.REGISTRATION:
            raise forms.ValidationError('Registration is not open at this time')
        if not self.assassin.squad is None:
            raise forms.ValidationError('You are already in a squad')
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

    def clean_gamecode(self):
        gamecode = self.cleaned_data.get('gamecode')
        if not gamecode is None:
            if self.game.code.lower() == gamecode.strip().lower():
                return gamecode.strip().lower()
        raise forms.ValidationError('Incorrect join code')

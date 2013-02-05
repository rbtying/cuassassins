from django import forms
from assassins_manager.models import *

class KillForm(forms.Form):
    """ Form to test and verify kills """

    def __init__(self, *args, **kwargs):
        self.assassin = kwargs.pop('assassin', None)
        super(KillForm, self).__init__(*args, **kwargs)
        self.squad = self.assassin.squad
        self.game = self.assassin.game

        qset = Assassin.objects.filter(game=self.game, alive=True).exclude(id=self.assassin.id).order_by('squad')
        
        self.fields['corpse'] = forms.ModelChoiceField(queryset=qset)
        self.fields['lifecode'] = forms.CharField(max_length=10)
        self.fields['report'] = forms.CharField(widget=forms.Textarea)
        self.fields['type'] = forms.IntegerField()
        self.fields['contract'] = forms.ModelChoiceField(queryset=Contract.objects.filter(game=self.game))
        self.fields.keyOrder = ['corpse', 'lifecode', 'report']

    def clean_report(self):
        if self.cleaned_data.get('report') == '':
            raise forms.ValidationError('Please enter a kill report')
        else:
            return self.cleaned_data.get('report')

    def clean_corpse(self):
        corpse = self.cleaned_data.get('corpse')
        if corpse is None:
            raise forms.ValidationError('Who did you kill?')
        else:
            return corpse

    def clean(self):
        corpse = self.cleaned_data.get('corpse')
        lifecode = self.cleaned_data.get('lifecode')
        if not lifecode is None:
            lifecode = lifecode.strip().lower()
        corpsecode = corpse.lifecode

        if not self.game.status == GameStatus.IN_PROGRESS:
            raise forms.ValidationError('Kills may only be reported when the game is in progress')

        if not self.assassin.alive:
            raise forms.ValidationError('Only living players can report kills')

        if not corpse.alive:
            raise forms.ValidationError('This corpse has already been reported')

        if lifecode == corpsecode.lower():
            if self.assassin.role == AssassinType.POLICE:
                if not corpse.assassin.role == AssassinType.DISAVOWED:
                    raise forms.ValidationError('Police may only kill disavowed players')

            forward = False
            try:
                # see if there are any forward contracts
                c = Contract.objects.get(game=self.game, holder=self.squad, target=corpse.squad, status=ContractStatus.ACTIVE)
                forward = True
            except Contract.DoesNotExist:
                c = None

            if c is None:
                try:
                    # see if the contract was reversed (ie self defense)
                    c = Contract.objects.get(game=self.game, holder=corpse.squad, target=self.squad, status=ContractStatus.ACTIVE)
                    forward = False
                except Contract.DoesNotExist:
                    c = None

            self.cleaned_data['contract'] = c

            # police can be killed only in self-defense
            if corpse.role == AssassinType.POLICE:
                self.cleaned_data['type'] = ReportType.SELF_DEFENSE
                self.cleaned_data['contract'] = None
                return self.cleaned_data

            # only people holding the contract can kill this guy, or self-defense
            if not c is None:
                if forward:
                    self.cleaned_data['type'] = ReportType.CONTRACT_KILL
                else:
                    self.cleaned_data['type'] = ReportType.SELF_DEFENSE

                self.cleaned_data['contract'] = c
                return self.cleaned_data

            if corpse.role == AssassinType.REGULAR:
                raise forms.ValidationError('You may only kill players in self-defense or in your contract')

            # anyone can kill disavowed people
            elif corpse.role == AssassinType.DISAVOWED:
                self.cleaned_data['type'] = ReportType.SANCTIONED_KILL
                self.cleaned_data['contract'] = None
                return self.cleaned_data
        else:
            raise forms.ValidationError('Please enter your corpse\'s lifecode')

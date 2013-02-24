from django import forms
from assassins_manager.models import Assassin, Squad, Contract
from columbia_util.models import ColumbiaUserProfile

class AssassinEditForm(forms.ModelForm):
    """ Form to edit assassin pictures in the details page """
    class Meta:
        model = ColumbiaUserProfile
        fields = ('image',)

    def clean_image(self):
        if not self.cleaned_data.get('image'):
            raise forms.ValidationError('You must upload an image')

        return self.cleaned_data.get('image')

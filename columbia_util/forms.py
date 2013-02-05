from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from django.conf import settings
from models import *
import services

class ColumbiaUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('username',)

    def clean_username(self):
        try:
            user = get_user_model().objects.get(username=self.cleaned_data['username'])
        except get_user_model().DoesNotExist:
            if services.verify_uni(self.cleaned_data['username']):
                return self.cleaned_data['username']
            else:
                raise forms.ValidationError(u'Please use your UNI for your username')

        raise forms.ValidationError(u'This username is already taken')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super(ColumbiaUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# class ColumbiaUserChangeForm(forms.ModelForm):
#     password = ReadOnlyPasswordHashField(label='Password', help_text='Raw passwords are not stored, so there is no way to see this user\'s password. You can change the password using <a href=\"password/\">this form</a>.')
# 
#     class Meta:
#         model = ColumbiaUser
# 
#     def clean_password(self):
#         return self.initial['password']
# 
#     def save(self, commit=True):
#         user = super(ColumbiaUserChangeForm, self).save(commit=False)
#         user.ldap_update()
#         if commit:
#             user.save()
#         return user

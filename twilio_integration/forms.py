from django import forms
from models import *
import re

class EditPhone(forms.ModelForm):
    changed = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def clean_phone_number(self):
        number = self.cleaned_data.get('phone_number')
        if not number is None:
            min_number = re.sub(r'\D', '', number)
            if min_number != number:
                raise forms.ValidationError('Please enter only numbers')
            else:
                return number
        else:
            raise forms.ValidationError('Please enter a phone number')
            

    def clean(self):
        if not self.instance.phone_number == self.cleaned_data.get('phone_number'):
            self.cleaned_data['changed'] = True
        else:
            self.cleaned_data['changed'] = False

        return self.cleaned_data
            
            
    class Meta:
        model = PhoneNumber
        fields = ('phone_number',)

class VerifyPhone(forms.Form):
    code = forms.CharField(max_length=6)

    def set_code(self, code):
        self.correct_code = code

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError('Please enter the code')
        if code.lower() == self.correct_code.lower():
            return code
        else:
            raise forms.ValidationError('Code does not match')

from django import forms
from .models import Direct

class DirectForm(forms.ModelForm):
    class Meta:
        model = Direct
        fields = ['text', 'photo']
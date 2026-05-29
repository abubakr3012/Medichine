from django import forms
from .models import Profile

class ProfileForm(forms.Form):
    age=forms.IntegerField()
    phone=forms.CharField(max_length=14)
    photo=forms.ImageField(required=False)

    
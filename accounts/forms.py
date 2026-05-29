from django import forms
from .models import Profile

class ProfileForm(forms.Form):
    user=forms.ModelChoiceField(
        queryset=Profile.objects.filter(role='doctor'),
        label='Doctor name',
        )
    age=forms.IntegerField()
    phone=forms.CharField(max_length=14)
    photo=forms.ImageField(required=False)

    
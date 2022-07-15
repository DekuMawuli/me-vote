from django import forms
from .models import Contestant


class ContestantForm(forms.ModelForm):
    class Meta:
        model = Contestant
        fields = ['position', 'full_name', 'profile_image']

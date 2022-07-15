from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Voter


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'role', 'password']


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        meta = CustomUser
        fields = UserChangeForm.Meta.fields


class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['level', 'program']

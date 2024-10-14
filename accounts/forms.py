from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=128, required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

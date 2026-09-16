# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser  # <-- Aquí le decimos que use nuestro modelo personalizado
        fields = UserCreationForm.Meta.fields # Mantiene los campos por defecto
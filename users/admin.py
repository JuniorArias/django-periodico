# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Registramos nuestro modelo personalizado usando el UserAdmin de Django
admin.site.register(CustomUser, UserAdmin)
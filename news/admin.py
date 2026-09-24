from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Post
from users.models import CustomUser

admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'autor')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


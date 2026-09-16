from django.contrib import admin
from .models import Post

admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'autor')

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
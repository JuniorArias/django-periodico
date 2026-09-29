from django.contrib import admin
from .models import Post, Comment, PostImage, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1  # Mostrar 1 formulario vacío para agregar imágenes


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'allow_comments']
    list_filter = ['created_at', 'allow_comments', 'author', 'category']
    search_fields = ['title', 'text', 'content']
    inlines = [PostImageInline]  # Permite agregar imágenes desde el admin


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'caption', 'order', 'created_at']


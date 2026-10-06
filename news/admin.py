from django.contrib import admin
from .models import Post, Comment, PostImage, Category, CategoryTranslation, Like, SiteConfig, Notification, PostTranslation

class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    verbose_name = "Traducción"
    verbose_name_plural = "Traducciones de esta categoría"

class PostTranslationInline(admin.TabularInline):
    """Permite editar traducciones de titulo y contenido desde el admin del post"""
    model = PostTranslation
    extra = 1
    verbose_name = "Traducción del Artículo"
    verbose_name_plural = "Traducciones de este Artículo"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryTranslationInline]

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1  # Mostrar 1 formulario vacío para agregar imágenes

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'allow_comments']
    list_filter = ['created_at', 'allow_comments', 'author', 'category']
    search_fields = ['title', 'text', 'content']
    inlines = [PostImageInline, PostTranslationInline]  # Permite agregar imágenes desde el admin

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'caption', 'order', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_url', 'primary_color', 'allow_registration', 'enable_multilanguage', 'default_language', 'updated_at']
    fieldsets = (
        ('Información General', {
            'fields': ('site_name', 'site_url', 'tagline', 'logo')
        }),
        ('Apariencia', {
            'fields': ('primary_color',)
        }),
        ('Permisos', {
            'fields': ('allow_registration',)
        }),
        ('Multi-Idioma', {
            'fields': ('enable_multilanguage', 'default_language'),
            'description': 'Controla el soporte de idiomas en la aplicación'
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'post', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']
    readonly_fields = ['created_at']
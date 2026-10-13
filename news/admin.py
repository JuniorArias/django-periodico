from django.contrib import admin
from tinymce.widgets import TinyMCE
from django import forms
from .models import Post, Comment, PostImage, Category, CategoryTranslation, Like, SiteConfig, Notification, PostTranslation


# ==========================================
# FORMULARIO PERSONALIZADO PARA SITECONFIG
# ==========================================
class SiteConfigForm(forms.ModelForm):
    """Formulario personalizado con color pickers para los 8 campos de color"""
    class Meta:
        model = SiteConfig
        fields = '__all__'
        widgets = {
            # --- Colores Modo Claro ---
            'light_primary_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'light_secondary_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'light_background_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'light_text_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            
            # --- Colores Modo Oscuro ---
            'dark_primary_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'dark_secondary_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'dark_background_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            'dark_text_color': forms.TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 40px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;'}),
            
            # --- Otros campos ---
            'site_url': forms.URLInput(attrs={'placeholder': 'https://miperiodico.com', 'style': 'width: 400px;'}),
            'site_name': forms.TextInput(attrs={'placeholder': 'Periódico Digital', 'style': 'width: 400px;'}),
            'tagline': forms.TextInput(attrs={'placeholder': 'Tu fuente de noticias', 'style': 'width: 400px;'}),
        }


# ==========================================
# ADMIN DE CATEGORÍAS
# ==========================================
class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    verbose_name = "Traducción"
    verbose_name_plural = "Traducciones de esta categoría"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryTranslationInline]


# ==========================================
# ADMIN DE POSTS
# ==========================================
class PostTranslationInline(admin.TabularInline):
    """Permite editar traducciones de titulo y contenido desde el admin del post"""
    model = PostTranslation
    extra = 1
    verbose_name = "Traducción del Artículo"
    verbose_name_plural = "Traducciones de este Artículo"


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1  # Mostrar 1 formulario vacío para agregar imágenes


# ==========================================
# ADMIN DE COMENTARIOS
# ==========================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']


# ==========================================
# ADMIN DE IMÁGENES DE POSTS
# ==========================================
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'caption', 'order', 'created_at']


# ==========================================
# ADMIN DE LIKES
# ==========================================
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']


# ==========================================
# ADMIN DE SITECONFIG (con color pickers)
# ==========================================
@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    form = SiteConfigForm
    
    # Mostramos solo lo esencial en la lista para no saturar
    list_display = ['site_name', 'site_url', 'allow_registration', 'updated_at']
    
    fieldsets = (
        ('Información General', {
            'fields': ('site_name', 'site_url', 'tagline', 'logo'),
            'description': 'Configuración básica e identidad del sitio'
        }),
        ('☀️ Colores del Modo Claro', {
            'fields': (
                'light_primary_color', 
                'light_secondary_color', 
                'light_background_color', 
                'light_text_color'
            ),
            'description': 'Paleta de colores que se aplicará cuando el usuario active el tema claro.'
        }),
        ('🌙 Colores del Modo Oscuro', {
            'fields': (
                'dark_primary_color', 
                'dark_secondary_color', 
                'dark_background_color', 
                'dark_text_color'
            ),
            'description': 'Paleta de colores que se aplicará cuando el usuario active el tema oscuro.'
        }),
        ('Permisos y Multi-Idioma', {
            'fields': ('allow_registration', 'enable_multilanguage', 'default_language'),
            'description': 'Control de acceso y configuración de idiomas'
        }),
    )


# ==========================================
# ADMIN DE NOTIFICACIONES
# ==========================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'post', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']
    readonly_fields = ['created_at']

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ['title', 'author', 'category', 'created_at', 'allow_comments']
    list_filter = ['created_at', 'allow_comments', 'author', 'category']
    search_fields = ['title', 'text', 'content']
    inlines = [PostImageInline, PostTranslationInline]
from django.db import models
from django.conf import settings
from django.urls import reverse


# 1. PRIMERO: Modelo Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Descripción opcional de la categoría")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class CategoryTranslation(modles.Model):
    """Permite infinitos idiomas para las categorías sin tocar el código"""
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='translations'
    )
    language_code = models.CharField(
        max_length=10, 
        help_text="Código del idioma (ej: 'es', 'en', 'fr', 'pt')"
    )
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['category', 'language_code']
        verbose_name = "Traducción de Categoría"
        verbose_name_plural = "Traducciones de Categorías"
    
    def __str__(self):
        return f"{self.category.name} ({self.language_code}): {self.name}"


# 2. SEGUNDO: Modelo Post
class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, help_text="Título del artículo")
    text = models.TextField(help_text="Resumen corto del artículo")
    content = models.TextField(help_text="Contenido completo del artículo")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, help_text="Imagen principal")
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allow_comments = models.BooleanField(default=True, help_text="Permitir comentarios en este artículo")

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


# 3. TERCERO: Modelo Comment
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        title = self.post.title[:30] if self.post.title else "Sin título"
        return f"Comentario de {self.author.username} en '{title}'"


# 4. CUARTO: Modelo PostImage
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/gallery/')
    caption = models.CharField(max_length=200, blank=True, help_text="Descripción opcional")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        title = self.post.title[:30] if self.post.title else "Sin título"
        return f"Imagen de {title}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario solo puede dar like una vez por artículo
        unique_together = ['post', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked '{self.post.title[:30]}'"

class SiteConfig(models.Model):
    """Configuración global del sitio (singleton)"""
    site_name = models.CharField(max_length=100, default='Periódico Digital')
    site_url = models.URLField(help_text='URL pública del sitio (ej: https://miperiodico.com)')
    tagline = models.CharField(max_length=200, blank=True, default='Tu fuente de noticias')
    logo = models.ImageField(upload_to='config/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#607D8B', help_text='Color hexadecimal (ej: #607D8B)')
    allow_registration = models.BooleanField(default=True, help_text='Permitir registro de nuevos usuarios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Sitio'
        verbose_name_plural = 'Configuración del Sitio'

    def __str__(self):
        return f"Configuración: {self.site_name}"

    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia (singleton)
        if not self.pk and SiteConfig.objects.exists():
            # Si ya existe, actualizar la primera instancia
            existing = SiteConfig.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

class Notification(models.Model):
    """Notificaciones in-app para usuarios"""
    NOTIFICATION_TYPES = [
        ('comment', 'Nuevo comentario'),
        ('reply', 'Nueva respuesta'),
        ('like', 'Nuevo like'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='Usuario que recibe la notificación'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        help_text='Usuario que generó la notificación'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Artículo relacionado (opcional)'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES,
        help_text='Tipo de notificación'
    )
    message = models.TextField(help_text='Mensaje de la notificación')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} para {self.recipient.username}"
from django.db import models
from django.conf import settings
from django.urls import reverse


# 1. PRIMERO: Modelo Category (debe ir antes de Post)
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
        # Generar slug automáticamente si no se proporciona
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# 2. SEGUNDO: Modelo Post
class Post(models.Model):
    # Usamos settings.AUTH_USER_MODEL en lugar de User directamente
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, help_text="Título del artículo")
    text = models.TextField(help_text="Resumen corto del artículo")
    content = models.TextField(help_text="Contenido completo del artículo")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, help_text="Imagen principal")
    
    # Relación con Category
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

    # Método crucial para que Django sepa a dónde redirigir después de crear/editar
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


# 3. TERCERO: Modelo Comment
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    
    # Usamos settings.AUTH_USER_MODEL aquí también
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
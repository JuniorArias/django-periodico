# news/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Descrición opcional de la categoría")

class Post(models.Model):
    # Un campo de texto para el contenido del artículo
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="Título del artículo")
    text = models.TextField(help_text="Resumen corto del artículo")
    content = models.TextField(help_text="Contenido completo del artículo")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allow_comments = models.BooleanField(default=True, help_text="Permitir comentrios en este artículo")

    class Meta:
        ordering = ['-created_at']
    # Este método le dice a Django cómo mostrar el objeto Admin y en la consola 
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args=[str(self.pk)])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Los más recientes primero

    def __str__(self):
        return f"Comentario de {self.author.username} en '{self.post.text[:30]}'"

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/gallery/')
    caption = models.CharField(max_length=200, blank=True, help_text="Descripción opcional")
    order = models.PositiveIntegerField(default=0, help_text="Orden e aparición")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Imagen de {self.post.title}"
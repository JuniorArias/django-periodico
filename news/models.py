# news/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings

class Post(models.Model):
    # Un campo de texto para el contenido del artículo
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Este método le dice a Django cómo mostrar el objeto Admin y en la consola 
    def __str__(self):
        return self.text[:50]

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
    
# news/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings

class Post(models.Model):
    # Un campo de texto para el contenido del artículo
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Este método le dice a Django cómo mostrar el objeto Admin y en la consola 
    def __str__(self):
        return self.text[:50]

    def get_absolute_url(self):
        return reverse("post_detail", args=[str(self.id)])
    
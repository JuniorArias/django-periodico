# news/serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del autor, no solo su ID numérico
    author = serializers.ReadOnlyField(source='author.username')
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'image', 'created_at'] # Campos a exponer en la API
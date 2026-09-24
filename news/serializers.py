# news/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

# Serializer para posts
class PostSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del autor, no solo su ID numérico
    author = serializers.ReadOnlyField(source='author.username')
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'image', 'created_at'] # Campos a exponer en la API

# Serializer para registro de usuarios
class UserRegistationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Asignar el grupo "readers" por defecto
        from django.contrib.auth.models import Group
        readers_group, created = Group.objects.get_or_create(name='readers')
        user.groups.add(readers_group)
        return user

class CurrentUserSerializer(serializers.ModelSerializer):
    can_write = serializers.SerializerMethodField()

    class Meta:
        model
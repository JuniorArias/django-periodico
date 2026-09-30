# news/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, PostImage, Category

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.count()

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']

# Serializer para posts
class PostSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del autor, no solo su ID numérico
    author = serializers.ReadOnlyField(source='author.username')
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    comment_count = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'text', 'content', 'image',
            'category', 'category_id', 'images', 'created_at', 'updated_at',
            'comment_count', 'allow_comments'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updaated_at'] # Campos a exponer en la API

    def get_comment_count(self, obj):
        try:
            return obj.comments.count()
        except Exception:
            return 0

# Serializer para registro de usuarios
class UserRegistrationSerializer(serializers.ModelSerializer):
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
        model = User
        fields = ['id', 'username', 'email', 'can_write']

    def get_can_write(self, obj):
        # Verifica si el usuario tiene permisos de esxritura
        return obj.has_perm('news.add_post') or obj.has_perm('news.change_post')

# Serializer simple para respuestas
"""class CommentReplySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
"""

# Serializer principal para comentarios
# Serializer simple para operaciones de detalle (GET individual, DELETE)
class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'post', 'created_at', 'updated_at']


# Serializer recursivo para listar comentarios con respuestas anidadas
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()
    
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent', 'text', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'post', 'created_at', 'updated_at']

    def get_replies(self, obj):
        replies = obj.replies.all().order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data
    
    # ✅ NUEVO: Método create explícito para manejar parent correctamente
    def create(self, validated_data):
        # validated_data ya contiene 'parent' si se proporcionó
        # Solo creamos el comentario con todos los datos
        return Comment.objects.create(**validated_data)
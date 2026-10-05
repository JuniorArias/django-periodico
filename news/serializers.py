from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Post, Comment, PostImage, Category, Like, SiteConfig, Notification
)

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


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
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
            'comment_count', 'allow_comments', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        try:
            return obj.comments.count()
        except Exception:
            return 0

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


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
        return obj.has_perm('news.add_post') or obj.has_perm('news.change_post')


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'post', 'created_at', 'updated_at']


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
        # ✅ Obtener las respuestas directas de este comentario
        replies = Comment.objects.filter(parent=obj).order_by('created_at')
        # ✅ Serializar recursivamente
        return CommentSerializer(replies, many=True, context=self.context).data


class CommentReplySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

class LikeSerializer(serializers.ModelSerializer):
    model = Like
    fields = ['id', 'post', 'user', 'created_at']
    read_only_fields = ['id', 'user', 'post', 'created_at']

class SiteConfigSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = SiteConfig
        fields = ['site_name', 'site_url', 'tagline', 'logo', 'primary_color', 'allow_registration']


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    post_title = serializers.ReadOnlyField(source='post.title')
    comment_id = serializers.SerializersMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_username', 
            'post', 'post_title', 'notification_type', 
            'message', 'is_read', 'created_at', 'comment_id'
        ]
        read_only_fields = ['id', 'recipient', 'sender', 'created_at']

        def get_comment_id(self, obj):
            if obj.notification_type in ['reply', 'comment']:
                comment = Comment.objects.filter(
                    post=obj.post,
                    author=obj.sender,
                    created_at__lte=obj.created_at
                ).order_by('-created_at').first()
            
                if comment:
                    return comment.id
            return None
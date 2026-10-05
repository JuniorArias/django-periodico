from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [

    path('posts/', views.PostListAPIView.as_view(), name='post_list_api'),
    path('posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('posts/<int:post_id>/comments/', views.CommentListAPIView.as_view(), name='comment_list_api'),
    path('comments/<int:pk>/', views.CommentDetailAPIView.as_view(), name='comment_detail_api'),
        # Rutas para galería de imágenes
    path('posts/<int:post_id>/images/', views.PostImageListAPIView.as_view(), name='post_image_list'),
    path('images/<int:pk>/', views.PostImageDetailAPIView.as_view(), name='post_image_detail'),
    path('posts/<int:post_id>/images/reorder/', views.PostImageReorderAPIView.as_view(), name='post_image_reorder'),
        # Categorías
    path('categories/', views.CategoryListAPIView.as_view(), name='category_list'),
    path('categories/<slug:slug>/posts/', views.CategoryPostsAPIView.as_view(), name='category_posts'),
        # Likes
    path('posts/<int:post_id>/like/', views.LikeToggleAPIView.as_view(), name='like_toggle'),
        # Configuración del sitio
    path('site-config/', views.SiteConfigAPIView.as_view(), name='site_config'),
        # Notificaciones
    path('notifications/', views.NotificationListAPIView.as_view(), name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.NotificationMarkAsReadAPIView.as_view(), name='notification_mark_read'),
    path('notifications/mark-all-read/', views.NotificationMarkAllAsReadAPIView.as_view(), name='notification_mark_all_read'),
    path('notifications/unread-count/', views.UnreadNotificationCountAPIView.as_view(), name='notification_unread_count'),
]
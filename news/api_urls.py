from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [

    path('posts/', views.PostListAPIView.as_view(), name='post_list_api'),
    path('posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('posts/<int:post_id>/comments/', views.CommeentListAPIView.as_view(), name='comment_list_api'),
    path('comments/<int:pk>/', views.CommentDetailAPIView.as_view(), name='comment_detail_api'),
]
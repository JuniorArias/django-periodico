from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [

    path('posts/', views.PostListAPIView.as_view(), name='post_list_api'),
    path('posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.UserRegistationView.as_view(), name='user_registation'),
    path('me/', views.CurrentUserSerializer.as_view(), name='current_user'),
]
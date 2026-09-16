# news/urls.py
from django.urls import path
from .views import (HomePageView, AboutPageView, PostDetailView,
                    PostCreateView, PostUpdateView, PostDeleteView, SignUpView)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('post/<int:pk>  /', PostDetailView.as_view(), name='post_detail'),
    path('new/', PostCreateView.as_view(), name='post_new'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
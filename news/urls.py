# news/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import tinymce_views
from . import views
from .views import (HomePageView, AboutPageView, PostDetailView,
                    PostCreateView, PostUpdateView, PostDeleteView, SignUpView)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('new/', PostCreateView.as_view(), name='post_new'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('api/', include('news.api_urls')),
    
    # API pública de estilos
    path('api/styles/', views.get_public_styles, name='get_public_styles'),
    path('api/reset-styles/', views.reset_all_styles, name='reset_all_styles'),
    # Editor Visual
    path('visual-editor/', views.visual_editor_view, name='visual_editor'),
    path('api/save-style/', views.save_element_style, name='save_element_style'),
    path('api/update-scope/', views.update_element_scope, name='update_element_scope'),
    path('api/save-theme/', views.save_theme, name='save_theme'),
    path('api/reset-theme/', views.reset_theme, name='reset_theme'),
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/', tinymce_views.tinymce_upload_image, name='tinymce_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
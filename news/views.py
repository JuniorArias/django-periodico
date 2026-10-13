# news/views.py
import traceback
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
import json

from rest_framework import generics, permissions, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError, APIException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.forms import CustomUserCreationForm
from .models import (
    Post, Comment, PostImage, Category, Like, SiteConfig, Notification, CustomStyle
)
from .permissions import IsAuthorOrEditor
from .serializers import (
    PostSerializer, UserRegistrationSerializer, CurrentUserSerializer, CommentSerializer, 
    CommentDetailSerializer, PostImageSerializer, CategorySerializer, LikeSerializer, SiteConfigSerializer,
    NotificationSerializer
)

# ==========================================
# VISTAS WEB (Frontend Django)
# ==========================================

def test_debug_view(request):
    try:
        # 1. Verificar variables de entorno
        debug_status = settings.DEBUG
        allowed_hosts = settings.ALLOWED_HOSTS
        
        # 2. Verificar conexión a base de datos
        post_count = Post.objects.count()
        last_post = Post.objects.last()
        
        return HttpResponse(f"""
            <h2>✅ Diagnóstico Exitoso</h2>
            <p><strong>DEBUG está:</strong> {debug_status}</p>
            <p><strong>ALLOWED_HOSTS:</strong> {allowed_hosts}</p>
            <p><strong>Total de Posts en BD:</strong> {post_count}</p>
            <p><strong>Último Post:</strong> {last_post.title if last_post else 'Ninguno'}</p>
            <hr>
            <p>Si ves esto, Django, la BD y las variables de entorno funcionan bien. El error está en tu plantilla HTML o en una vista específica.</p>
        """)
    except Exception as e:
        # Si algo falla, esto mostrará el error REAL en el navegador
        return HttpResponse(f"""
            <h2>❌ Error Encontrado</h2>
            <p><strong>Excepción:</strong> {e}</p>
            <pre style="background:#fee; padding:15px; border:1px solid red; overflow:auto;">
{traceback.format_exc()}
            </pre>
        """, status=500)

class HomePageView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'all_posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(text__icontains=query) | Q(author__username__icontains=query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        current_page = context['page_obj'].number
        total_pages = context['page_obj'].paginator.num_pages

        if total_pages <= 7:
            context['page_range'] = context['page_obj'].paginator.page_range
        else:
            start = max(1, current_page - 2)
            end = min(total_pages, current_page + 2)
            context['page_range'] = range(start, end + 1)
        return context


class AboutPageView(TemplateView):
    template_name = 'about.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        obj = self.get_object()
        context['can_edit'] = (user == obj.author) or user.has_perm('news.change_post') or user.is_superuser
        context['can_delete'] = (user == obj.author) or user.has_perm('news.delete_post') or user.is_superuser
        return context



class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = 'login'
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'text', 'content', 'image', 'allow_comments']

    def test_func(self):
        user = self.request.user
        return user.has_perm('news.add_post') or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para crear artículos.')
        return redirect('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = 'login'
    model = Post
    template_name = 'post_update.html'
    fields = ['title', 'text', 'content', 'image', 'allow_comments']

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return (obj.author == user) or user.has_perm('news.change_post') or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para editar este artículo.')
        return redirect('home')


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = 'login'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return (obj.author == user) or user.has_perm('news.delete_post') or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para borrar este artículo.')
        return redirect('home')


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


# ==========================================
# VISTAS API (REST Framework para Flutter)
# ==========================================

class PostPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostListAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all().select_related('author', 'category')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
    pagination_class = PostPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text', 'content', 'category__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_superuser and not self.request.user.has_perm('news.add_post'):
            raise PermissionDenied("No tienes permisos para crear artículos. Tu cuenta es de solo lectura.")
        serializer.save(author=self.request.user)

    def get_parser_classes(self):
        return [MultiPartParser, FormParser, JSONParser]


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrEditor]
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        if not self.get_object_permissions():
            raise PermissionDenied("No tienes permisos para editar este artículo.")
        serializer.save()

    def get_object_permissions(self):
        obj = self.get_object()
        user = self.request.user
        if user.is_superuser:
            return True
        if obj.author == user:
            return True
        if user.has_perm('news.change_post'):
            return True
        return False

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        obj = self.get_object()
        user = self.request.user
        if not (user.is_superuser or obj.author == user or user.has_perm('news.delete_post')):
            raise PermissionDenied("No tienes permisos para borrar este artículo.")
        instance.delete()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente. Tu cuenta tiene permisos de solo lectura.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)


class CommentListAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id, 
            parent__isnull=True
        ).select_related('author').prefetch_related(
            'replies__author',
            'replies__replies__author',
            'replies__replies__replies__author',
        ).order_by('created_at')

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("El artículo no existe")
        
        if not post.allow_comments:
            raise PermissionDenied("Los comentarios están deshabilitados")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        parent = serializer.validated_data.get('parent')
        
        if parent and parent.post_id != post.id:
            raise ValidationError("El comentario padre no pertenece a este artículo")
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            parent=parent,
            text=serializer.validated_data['text']
        )
        
        # Crear notificación
        if parent:
            if parent.author != request.user:
                Notification.objects.create(
                    recipient=parent.author,
                    sender=request.user,
                    post=post,
                    notification_type='reply',
                    message=f'{request.user.username} respondió a tu comentario en "{post.title}"'
                )
        else:
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    post=post,
                    notification_type='comment',
                    message=f'{request.user.username} comentó en tu artículo "{post.title}"'
                )
        
        output_serializer = self.get_serializer(comment)
        return Response(output_serializer.data, status=201)


class CommentDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all().select_related('author')
    serializer_class = CommentDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("No tienes permiso para borrar este comentario")
        instance.delete()


class PostImageListAPIView(generics.ListCreateAPIView):
    serializer_class = PostImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return PostImage.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        try:
            post_id = self.kwargs.get('post_id')
            post = Post.objects.get(id=post_id)
            
            if not (self.request.user.is_superuser or 
                    post.author == self.request.user or 
                    self.request.user.has_perm('news.change_post')):
                raise PermissionDenied("No tienes permiso para agregar imágenes a este artículo")
            
            serializer.save(post=post)
            
        except Post.DoesNotExist:
            raise NotFound("El artículo no existe")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ ERROR AL SUBIR IMAGEN: {error_detail}")
            raise APIException(f"Error al procesar la imagen: {str(e)}")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ ERROR EN CREATE: {error_detail}")
            return Response(
                {'error': str(e), 'detail': error_detail}, 
                status=500
            )


class PostImageDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        post = instance.post
        user = self.request.user
        
        if not (user.is_superuser or 
                post.author == user or 
                user.has_perm('news.delete_post')):
            raise PermissionDenied("No tienes permiso para eliminar esta imagen")
        
        instance.delete()


class PostImageReorderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            
            if not (request.user.is_superuser or 
                    post.author == request.user or 
                    request.user.has_perm('news.change_post')):
                return Response({'error': 'No tienes permiso'}, status=403)
            
            images_data = request.data.get('images', [])
            
            for img_data in images_data:
                image_id = img_data.get('id')
                new_order = img_data.get('order')
                
                if image_id and new_order is not None:
                    PostImage.objects.filter(id=image_id, post=post).update(order=new_order)
            
            return Response({'success': True, 'message': 'Imágenes reordenadas'})
        except Post.DoesNotExist:
            return Response({'error': 'Artículo no encontrado'}, status=404)


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Post.objects.filter(category__slug=category_slug).select_related('author', 'category')


class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Artículo no encontrado'}, status=404)

        existing_like = Like.objects.filter(post=post, user=request.user).first()

        if existing_like:
            existing_like.delete()
            return Response({
                'liked': False,
                'like_count': post.likes.count(),
                'message': 'Like eliminado'
            })
        else:
            Like.objects.create(post=post, user=request.user)

            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    post=post,
                    notification_type='like',
                    message=f'{request.user.username} dio like a tu artículo "{post.title}"'
                )
                
            return Response({
                'liked': True,
                'like_count': post.likes.count(),
                'message': 'Like agregado'
            })


class SiteConfigAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        config = SiteConfig.objects.first()

        if not config:
            config = SiteConfig.objects.create(
                site_name='Periódico Digital',
                site_url=request.build_absolute_uri('/')[:-1],
                tagline='Tu fuente de noticias'
            )

        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id, 
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({'success': True, 'message': 'Notificación marcada como leída'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notificación no encontrada'}, status=404)


class NotificationMarkAllAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True)
        return Response({'success': True, 'message': 'Todas las notificaciones marcadas como leídas'})


class UnreadNotificationCountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        return Response({'unread_count': count})


# ==========================================
# EDITOR VISUAL (Tipo Elementor)
# ==========================================

@staff_member_required
def visual_editor_view(request):
    """Editor visual tipo Elementor con filtros por scope"""
    scope_filter = request.GET.get('scope', 'all')
    
    if scope_filter == 'all':
        styles = CustomStyle.objects.all()
    else:
        styles = CustomStyle.objects.filter(scope=scope_filter)
    
    # Agrupar por scope y categoría
    grouped = {}
    for style in styles:
        if style.scope not in grouped:
            grouped[style.scope] = {}
        if style.category not in grouped[style.scope]:
            grouped[style.scope][style.category] = []
        
        grouped[style.scope][style.category].append({
            'id': style.id,
            'selector': style.selector,
            'friendly_name': style.friendly_name,
            'styles': style.styles,
            'scope': style.scope
        })
    
    return render(request, 'admin/visual_editor.html', {
        'grouped': grouped,
        'current_scope': scope_filter,
        'title': 'Editor Visual Completo'
    })


@csrf_exempt
@staff_member_required
@require_POST
def save_element_style(request):
    """Guarda o crea estilos de un elemento basado en su selector CSS"""
    try:
        data = json.loads(request.body)
        selector = data.get('selector', '')
        styles = data.get('styles', {})
        friendly_name = data.get('friendly_name', selector)
        scope = data.get('scope', 'global')
        category = data.get('category', 'layout')
        
        if not selector:
            return JsonResponse({'success': False, 'error': 'Selector vacío'}, status=400)
        
        # ✅ Crear o actualizar el estilo basado en el selector
        style_obj, created = CustomStyle.objects.update_or_create(
            selector=selector,
            defaults={
                'friendly_name': friendly_name,
                'styles': styles,
                'scope': scope,
                'category': category
            }
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'message': 'Estilo creado' if created else 'Estilo actualizado'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@staff_member_required
@require_POST
def reset_all_styles(request):
    """Elimina todos los estilos personalizados"""
    try:
        deleted_count = CustomStyle.objects.all().count()
        CustomStyle.objects.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} estilos eliminados',
            'deleted': deleted_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@staff_member_required
@require_POST
def update_element_scope(request):
    """Actualiza el scope (alcance) de un elemento"""
    try:
        data = json.loads(request.body)
        style_id = data.get('id')
        new_scope = data.get('scope')
        
        style = CustomStyle.objects.get(id=style_id)
        style.scope = new_scope
        style.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Alcance actualizado'
        })
    except CustomStyle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Elemento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# news/views.py - Agrega esta vista

@csrf_exempt
@staff_member_required
@require_POST
def save_theme(request):
    """Guarda la configuración del tema"""
    try:
        data = json.loads(request.body)
        mode = data.get('mode', 'light')
        colors = data.get('colors', {})
        
        config = SiteConfig.objects.first()
        if not config:
            config = SiteConfig.objects.create()
        
        # Actualizar colores según el modo
        if mode == 'dark':
            config.dark_primary_color = colors.get('primary', config.dark_primary_color)
            config.dark_secondary_color = colors.get('secondary', config.dark_secondary_color)
            config.dark_background_color = colors.get('background', config.dark_background_color)
            config.dark_text_color = colors.get('text', config.dark_text_color)
        else:
            config.light_primary_color = colors.get('primary', config.light_primary_color)
            config.light_secondary_color = colors.get('secondary', config.light_secondary_color)
            config.light_background_color = colors.get('background', config.light_background_color)
            config.light_text_color = colors.get('text', config.light_text_color)
        
        config.save()
        
        return JsonResponse({'success': True, 'message': 'Tema guardado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@staff_member_required
@require_POST
def reset_theme(request):
    """Restaura el tema por defecto"""
    try:
        config = SiteConfig.objects.first()
        if config:
            config.light_primary_color = '#607D8B'
            config.light_secondary_color = '#FF9800'
            config.light_background_color = '#F8F9FA'
            config.light_text_color = '#212529'
            config.dark_primary_color = '#37474F'
            config.dark_secondary_color = '#FFB74D'
            config.dark_background_color = '#1A1A1A'
            config.dark_text_color = '#E0E0E0'
            config.save()
        
        return JsonResponse({'success': True, 'message': 'Tema restaurado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_styles(request):
    """API pública para que Flutter lea los estilos"""
    styles = CustomStyle.objects.filter(scope__in=['public', 'global'])
    
    styles_dict = {}
    for style in styles:
        styles_dict[style.selector] = style.styles
    
    return Response({
        'success': True,
        'styles': styles_dict
    })
# news/views.py
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import generics, permissions, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from users.forms import CustomUserCreationForm
from .models import Post, Comment, PostImage, Category
from .permissions import IsAuthorOrEditor
from .serializers import PostSerializer, UserRegistrationSerializer, CurrentUserSerializer, CommentSerializer, CommentDetailSerializer, PostImageSerializer, CategorySerializer


# ==========================================
# VISTAS WEB (Frontend Django)
# ==========================================

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
        # Agregamos is_superuser para que el admin siempre tenga acceso en la web
        context['can_edit'] = (user == obj.author) or user.has_perm('news.change_post') or user.is_superuser
        context['can_delete'] = (user == obj.author) or user.has_perm('news.delete_post') or user.is_superuser
        return context


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = 'login'
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'text', 'content', 'image', 'allow_comments'] # Agregué 'image' para que funcione desde la web también

    def test_func(self):
        """Solo permite crear posts a ususarios con permiso o superusuarios"""
        user = self.request.user
        return user.has_perm('news.add_post') or user.is_superuser

    def hadle_no_permission(self):
        """Mesaje personalizado cuando no tiene permisos"""
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
        from django.contrib import messages
        messages.error(self.request, 'No tienes permisos para editar este artículo.')
        from django.shortcuts import redirect
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
        from django.contrib import messages
        messages.error(self.request, 'No tienes permisos para borrar este artículo.')
        from django.shortcuts import redirect
        return redirect('home')


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


# ==========================================
# VISTAS API (REST Framework para Flutter)
# ==========================================

# Clase de paginación para los posts
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
    search_fields = ['title', 'text', 'content']
    ordering_fileds = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por categoria si se proporciona el parametro
        category_slug = self.request.query_params.get('category')
        """queryset = Post.objects.all().order_by('-id')
        search_query = self.request.query_params.get('q', None)

        if search_query:
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )"""
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def perform_create(self, serializer):
        # Validación explícita: Superusuarios o usuarios con permiso 'add_post'
        if not self.request.user.is_superuser and not self.request.user.has_perm('news.add_post'):
            raise PermissionDenied("No tienes permisos para crear artículos. Tu cuenta es de solo lectura.")
        serializer.save(author=self.request.user)

    def get_parser_classes(self): # ✅ CORREGIDO: antes decía get_parder_classes
        from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
        return [MultiPartParser, FormParser, JSONParser]


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrEditor]
    authentication_classes = [TokenAuthentication]
    
    # ✅ Aceptar todos los métodos necesarios incluyendo PATCH
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        """
        Actualizar el post verificando permisos
        """
        # Verificar permisos usando IsAuthorOrEditor
        if not self.get_object_permissions():
            raise PermissionDenied("No tienes permisos para editar este artículo.")
        
        # Guardar el post actualizado
        serializer.save()

    def get_object_permissions(self):
        """
        Verificar si el usuario tiene permisos para editar/borrar este objeto
        """
        obj = self.get_object()
        user = self.request.user
        
        # Superusuarios siempre pueden
        if user.is_superuser:
            return True
        
        # El autor puede editar
        if obj.author == user:
            return True
        
        # Usuarios con permisos específicos pueden
        if user.has_perm('news.change_post'):
            return True
        
        return False

    def update(self, request, *args, **kwargs):
        """
        Manejar tanto PUT como PATCH
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Manejar específicamente PATCH (actualización parcial)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        Eliminar el post verificando permisos
        """
        obj = self.get_object()
        user = self.request.user
        
        # Verificar permisos
        if not (user.is_superuser or obj.author == user or user.has_perm('news.delete_post')):
            raise PermissionDenied("No tienes permisos para borrar este artículo.")
        
        instance.delete()


class UserRegistrationView(generics.CreateAPIView): # ✅ CORREGIDO: antes decía UserRegistationView
    """
    Permite a los usuarios registrarse.
    Por defecto, se les asigna el grupo 'readers' (solo lectura).
    """
    serializer_class = UserRegistrationSerializer # ✅ CORREGIDO
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
    """
    Devuelve información del usuario autenticado actual, incluyendo sus permisos.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)

# Lista de comentarios de un post específico
class CommentListAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id, 
            parent__isnull=True
        ).select_related('author').prefetch_related('replies__author').order_by('created_at')

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("El artículo no existe")
        
        if not post.allow_comments:
            raise PermissionDenied("Los comentarios están deshabilitados")
        
        # Validar el serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener el parent si existe
        parent = serializer.validated_data.get('parent')
        
        # Validar que el parent pertenezca al mismo post
        if parent and parent.post_id != post.id:
            raise ValidationError("El comentario padre no pertenece a este artículo")
        
        # Crear el comentario manualmente
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            parent=parent,
            text=serializer.validated_data['text']
        )
        
        # Serializar la respuesta
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
            
            # Verificar permisos
            if not (self.request.user.is_superuser or 
                    post.author == self.request.user or 
                    self.request.user.has_perm('news.change_post')):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permiso para agregar imágenes a este artículo")
            
            # Guardar la imagen
            serializer.save(post=post)
            
        except Post.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("El artículo no existe")
        except Exception as e:
            # Capturar cualquier otro error y mostrarlo
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ ERROR AL SUBIR IMAGEN: {error_detail}")
            from rest_framework.exceptions import APIException
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
        
        # Verificar permisos
        if not (user.is_superuser or 
                post.author == user or 
                user.has_perm('news.delete_post')):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para eliminar esta imagen")
        
        instance.delete()


class PostImageReorderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            
            # Verificar permisos
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
    """Lista todas las categorias con su contador de posts"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryPostsAPIView(generics.ListAPIView):
    """Lista todos los posts de una categoria específica"""
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Post.objects.filter(category__slug=category_slug).select_related('author', 'category')
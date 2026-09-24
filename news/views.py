# news/views.py
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.forms import CustomUserCreationForm
from .models import Post
from .permissions import IsAuthorOrEditor
from .serializers import PostSerializer, UserRegistrationSerializer, CurrentUserSerializer


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
    fields = ['text', 'image'] # Agregué 'image' para que funcione desde la web también

    def test_func(self):
        """Solo permite crear posts a ususarios con permiso o superusuarios"""
        user = self.request.user
        return user.has_perm('news.add_post') or user.is_superuser

    def hadle_no_permission(self):
        """Mesaje personalizado cuando no tiene permisos"""
        messages.error(self.request, 'No tienes permisos para crear artículos. Tu cuenta es de solo lectura.')
        return redirect('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = 'login'
    model = Post
    template_name = 'post_update.html'
    fields = ['text', 'image']

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

class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-id')
        search_query = self.request.query_params.get('q', None)

        if search_query:
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )
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
# news/views.py
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.forms import CustomUserCreationForm
from django.db.models import Q
from .models import Post

class HomePageView(ListView): # <-- Cambiamos a Listview
    model = Post
    template_name = 'index.html'
    context_object_name = 'all_posts' # <-- Nombre de la lista de datos
    paginate_by = 5

    # 1. Sobrescribimos get_queryset para filtrar por búsqueda
    def get_queryset(self):
        queryset= super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            # Filtramos los post cuyo texto contenga la consulta
            queryset = queryset.filter(text__icontains=query)

        return queryset
    
    # 2. Actualizamos el contexto para pasr la consulta a la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Guardamos la consulta para mostrarla en la plantilla
        context['query'] = self.request.GET.get('q', '')

        current_page = context['page_obj'].number
        total_pages = context['page_obj'].paginator.num_pages

        # Si hay pocas páginas (menos de 7), mostramos todas
        if total_pages <=7:
            context['page_range'] = context['page_obj'].paginator.page_range
        else:
            # Si hay muchas, mostramos un "ventana" de 5 números alrededor de la actual
            start = max(1, current_page - 2)
            end = min(total_pages, current_page + 2)
            context['page_range'] = range(start, end + 1)

        return context

class AboutPageView(TemplateView):
    template_name = 'about.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    # 1. Sobrescribir el contexto para pasar los permisos
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        obj =self.get_object()

        context['can_edit'] = (user == obj.author) or user.has_perm('news.change_post')
        context['can_delete'] = (user == obj.author) or user.has_perm('news.delete_post')

        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Post
    template_name = 'post_new.html'
    fields = ['text'] # Le decimos a Django qué campos del modelo queremos en el formulario

    # Este método asigna el autor en secreto
    def form_valid(self, form):
        form.instance.author = self.request.user # Asigna el usuario logueado
        return super().form_valid(form) # Guarda el formulario

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Post
    template_name = 'post_update.html'
    fields = ['text']

    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        return (obj.author == user) or user.has_perm('news.change_post')
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = 'login'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        return (obj.author == user) or user.has_perm('news.delete_post')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
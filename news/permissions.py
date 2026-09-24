# news/permissions.py
from rest_framework import permissions

class IsAuthorOrEditor(permissions.BasePermission):
    """
    Permiso personalizado: 
    - Cualquiera puede leer (GET, HEAD, OPTIONS).
    - Solo el autor o usuarios con permisos de 'change_post' o 'delete_post' pueden editar/borrar.
    """
    def has_object_permission(self, request, view, obj):
        # Métodos seguros (lectura) siempre permitidos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Métodos de escritura (PUT, PATCH, DELETE) requieren se el autor o tener permisos
        return(
            obj.author == request.user or
            request.user.has_perm('news.charge_post') or
            request.user.has_perm('news.delete_post') or
            request,user.is_superuser
        )
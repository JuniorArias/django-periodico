from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

@csrf_exempt
@staff_member_required
def tinymce_upload_image(request):
    """Maneja la subida de imágenes desde TinyMCE"""
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            return JsonResponse({'error': 'Tipo de archivo no permitido'}, status=400)
        
        # Validar tamaño (máximo 5MB)
        if image.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'La imagen es muy grande (máx 5MB)'}, status=400)
        
        # Generar nombre único
        ext = os.path.splitext(image.name)[1]
        filename = f"tinymce/{uuid.uuid4().hex}{ext}"
        
        # Guardar archivo
        file_path = default_storage.save(filename, ContentFile(image.read()))
        file_url = default_storage.url(file_path)
        
        return JsonResponse({'location': file_url})
    
    return JsonResponse({'error': 'No se proporcionó archivo'}, status=400)
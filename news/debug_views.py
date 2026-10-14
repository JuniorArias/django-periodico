from django.shortcuts import render
from django.http import HttpResponse
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from .models import Post
import traceback

def debug_post_detail(request, post_id):
    """Vista de diagnóstico para encontrar errores en post_detail.html"""
    try:
        post = Post.objects.get(id=post_id)
        
        # Intentar renderizar el template
        context = {
            'post': post,
            'can_edit': True,
            'can_delete': True,
        }
        
        return render(request, 'post_detail.html', context)
        
    except Post.DoesNotExist:
        return HttpResponse(f"""
            <h2>❌ Post no encontrado</h2>
            <p>No existe un post con ID {post_id}</p>
        """, status=404)
        
    except TemplateDoesNotExist as e:
        return HttpResponse(f"""
            <h2>❌ Template no encontrado</h2>
            <p><strong>Error:</strong> {e}</p>
            <p>Verifica que el archivo <code>templates/post_detail.html</code> exista.</p>
        """, status=404)
        
    except TemplateSyntaxError as e:
        return HttpResponse(f"""
            <h2>❌ Error de sintaxis en template</h2>
            <p><strong>Error:</strong> {e}</p>
            <pre style="background:#fee; padding:20px; border:2px solid #c00;">
{traceback.format_exc()}
            </pre>
        """, status=500)
        
    except Exception as e:
        return HttpResponse(f"""
            <h2>❌ Error inesperado</h2>
            <p><strong>Tipo:</strong> {type(e).__name__}</p>
            <p><strong>Mensaje:</strong> {e}</p>
            <pre style="background:#fee; padding:20px; border:2px solid #c00;">
{traceback.format_exc()}
            </pre>
        """, status=500)
# news/context_processors.py

from .models import SiteConfig

def site_config(request):
    """Configuración del sitio con soporte de temas"""
    try:
        config = SiteConfig.objects.first()
        
        if config:
            # Detectar tema activo (desde cookie, header o default)
            theme = request.COOKIES.get('theme_mode', 'light')
            
            if theme == 'dark':
                primary = config.dark_primary_color
                secondary = config.dark_secondary_color
                background = config.dark_background_color
                text = config.dark_text_color
            else:
                primary = config.light_primary_color
                secondary = config.light_secondary_color
                background = config.light_background_color
                text = config.light_text_color
            
            return {
                'site_config': config,
                'site_name': config.site_name,
                'primary_color': primary,
                'secondary_color': secondary,
                'background_color': background,
                'text_color': text,
                'current_theme': theme,
                # Pasar todos los colores para el panel de personalización
                'light_primary': config.light_primary_color,
                'light_secondary': config.light_secondary_color,
                'light_background': config.light_background_color,
                'light_text': config.light_text_color,
                'dark_primary': config.dark_primary_color,
                'dark_secondary': config.dark_secondary_color,
                'dark_background': config.dark_background_color,
                'dark_text': config.dark_text_color,
            }
        else:
            return {
                'site_config': None,
                'site_name': 'Periódico Digital',
                'primary_color': '#607D8B',
                'secondary_color': '#FF9800',
                'background_color': '#F8F9FA',
                'text_color': '#212529',
                'current_theme': 'light',
            }
    except Exception as e:
        return {
            'site_config': None,
            'site_name': 'Periódico Digital',
            'primary_color': '#607D8B',
            'secondary_color': '#FF9800',
            'background_color': '#F8F9FA',
            'text_color': '#212529',
            'current_theme': 'light',
        }
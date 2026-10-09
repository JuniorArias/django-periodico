from .models import SiteConfig

def site_config(request):
    """
    Hace que la configuración del sitio esté disponible 
    en todos los templates (incluido el admin)
    """
    try:
        config = SiteConfig.objects.first()
        return {
            'site_config': config,
            'primary_color': config.primary_color if config else '#607D8B',
            'site_name': config.site_name if config else 'Periódico Digital',
        }
    except:
        return {
            'site_config': None,
            'primary_color': '#607D8B',
            'site_name': 'Periódico Digital',
        }
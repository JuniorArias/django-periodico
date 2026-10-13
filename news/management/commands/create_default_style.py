from django.core.management.base import BaseCommand
from news.models import CustomStyle

class Command(BaseCommand):
    help = 'Crea los estilos personalizables por defecto para Admin y Sitio Público'

    def handle(self, *args, **kwargs):
        default_styles = [
            # ========================================
            # ADMIN
            # ========================================
            {
                'selector': '#header',
                'friendly_name': 'Header del Admin',
                'scope': 'admin',
                'category': 'layout',
                'styles': {
                    'background': '#607D8B',
                    'color': '#ffffff',
                    'padding': '10px 20px',
                }
            },
            {
                'selector': '#nav-sidebar',
                'friendly_name': 'Sidebar del Admin',
                'scope': 'admin',
                'category': 'layout',
                'styles': {
                    'background': '#f8f9fa',
                    'color': '#212529',
                    'width': '240px',
                }
            },
            {
                'selector': '.module',
                'friendly_name': 'Tarjetas del Admin',
                'scope': 'admin',
                'category': 'layout',
                'styles': {
                    'background': '#ffffff',
                    'border': '1px solid #dee2e6',
                    'border-radius': '6px',
                }
            },
            {
                'selector': 'input[type=submit], .button',
                'friendly_name': 'Botones del Admin',
                'scope': 'admin',
                'category': 'buttons',
                'styles': {
                    'background': '#607D8B',
                    'color': '#ffffff',
                    'border-radius': '4px',
                }
            },
            
            # ========================================
            # SITIO PÚBLICO
            # ========================================
            {
                'selector': '.public-header',
                'friendly_name': 'Header Público',
                'scope': 'public',
                'category': 'navigation',
                'styles': {
                    'background': '#607D8B',
                    'color': '#ffffff',
                    'padding': '20px',
                    'box-shadow': '0 2px 10px rgba(0,0,0,0.1)',
                }
            },
            {
                'selector': '.public-nav a',
                'friendly_name': 'Links de Navegación',
                'scope': 'public',
                'category': 'navigation',
                'styles': {
                    'color': '#ffffff',
                    'font-size': '16px',
                    'font-weight': '500',
                }
            },
            {
                'selector': '.post-card',
                'friendly_name': 'Tarjetas de Artículos',
                'scope': 'public',
                'category': 'cards',
                'styles': {
                    'background': '#ffffff',
                    'border-radius': '12px',
                    'box-shadow': '0 4px 15px rgba(0,0,0,0.1)',
                    'padding': '20px',
                    'margin-bottom': '20px',
                }
            },
            {
                'selector': '.post-title',
                'friendly_name': 'Título de Artículo',
                'scope': 'public',
                'category': 'typography',
                'styles': {
                    'color': '#212529',
                    'font-size': '24px',
                    'font-weight': '700',
                    'margin-bottom': '10px',
                }
            },
            {
                'selector': '.post-meta',
                'friendly_name': 'Meta Info (Autor, Fecha)',
                'scope': 'public',
                'category': 'typography',
                'styles': {
                    'color': '#6c757d',
                    'font-size': '14px',
                }
            },
            {
                'selector': '.btn-primary',
                'friendly_name': 'Botón Primario Público',
                'scope': 'public',
                'category': 'buttons',
                'styles': {
                    'background': '#607D8B',
                    'color': '#ffffff',
                    'border-radius': '8px',
                    'padding': '12px 24px',
                    'font-weight': '600',
                }
            },
            {
                'selector': '.btn-secondary',
                'friendly_name': 'Botón Secundario Público',
                'scope': 'public',
                'category': 'buttons',
                'styles': {
                    'background': '#FF9800',
                    'color': '#ffffff',
                    'border-radius': '8px',
                    'padding': '12px 24px',
                }
            },
            {
                'selector': 'body',
                'friendly_name': 'Fondo General del Sitio',
                'scope': 'public',
                'category': 'colors',
                'styles': {
                    'background': '#f8f9fa',
                    'color': '#212529',
                }
            },
            {
                'selector': '.footer',
                'friendly_name': 'Footer',
                'scope': 'public',
                'category': 'layout',
                'styles': {
                    'background': '#343a40',
                    'color': '#ffffff',
                    'padding': '40px 20px',
                }
            },
            
            # ========================================
            # GLOBAL (Admin + Público)
            # ========================================
            {
                'selector': 'a',
                'friendly_name': 'Enlaces Globales',
                'scope': 'global',
                'category': 'typography',
                'styles': {
                    'color': '#FF9800',
                    'text-decoration': 'none',
                }
            },
            {
                'selector': 'a:hover',
                'friendly_name': 'Enlaces Hover',
                'scope': 'global',
                'category': 'typography',
                'styles': {
                    'color': '#E68900',
                }
            },
        ]

        for style_data in default_styles:
            obj, created = CustomStyle.objects.update_or_create(
                selector=style_data['selector'],
                defaults=style_data
            )
            status = 'Creado' if created else 'Actualizado'
            self.stdout.write(self.style.SUCCESS(f'✓ {status}: {style_data["friendly_name"]} [{style_data["scope"]}]'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(default_styles)} estilos configurados'))
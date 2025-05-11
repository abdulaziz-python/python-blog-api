# ads/apps.py
from django.apps import AppConfig


class AdsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ads'
    
    def ready(self):
        import ads.signals  # Import signals to ensure they are registered
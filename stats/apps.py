# stats/apps.py
from django.apps import AppConfig


class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stats'
    
    def ready(self):
        import stats.signals  # Import signals to ensure they are registered
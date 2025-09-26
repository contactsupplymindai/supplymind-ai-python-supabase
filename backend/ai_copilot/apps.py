from django.apps import AppConfig


class AiCopilotConfig(AppConfig):
    """Django app configuration for AI Copilot microservice."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_copilot'
    verbose_name = 'AI Copilot'
    
    def ready(self):
        """Initialize AI models and services when Django starts."""
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass

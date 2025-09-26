from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Orders Management'
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import orders.signals  # noqa F401
        except ImportError:
            pass

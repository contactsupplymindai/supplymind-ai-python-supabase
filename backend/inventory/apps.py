from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Django app configuration for Inventory Management.
    
    This app provides comprehensive REST API endpoints for inventory management
    using shared models connected to Supabase database.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Inventory Management'
    
    def ready(self):
        """
        Initialize the app when Django starts.
        
        This method is called once Django has loaded all apps.
        It's the place to register signals, perform startup checks,
        or any other initialization that needs to happen when the app loads.
        """
        # Import signals if any (currently none defined)
        # import inventory.signals
        
        # Perform any startup checks
        self._check_required_packages()
        
        # Log successful initialization
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Inventory Management app initialized successfully')
    
    def _check_required_packages(self):
        """
        Check if required packages are installed.
        """
        required_packages = [
            'rest_framework',
            'django_filters',
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            import warnings
            warnings.warn(
                f"Missing required packages for inventory app: {', '.join(missing_packages)}. "
                "Please install them for full functionality."
            )

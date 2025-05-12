from django.apps import AppConfig

class OtherVendorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'other_vendors'

    def ready(self):
        import other_vendors.signals  # Import signals here


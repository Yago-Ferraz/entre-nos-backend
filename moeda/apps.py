from django.apps import AppConfig


class MoedaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moeda'

    def ready(self):
        import moeda.signals

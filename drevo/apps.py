from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save


class DrevoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drevo'
    #

    def ready(self):
        import drevo.signals

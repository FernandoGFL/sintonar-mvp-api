from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sintonar.apps.authentication'

    def ready(self):
        import sintonar.apps.authentication.signals

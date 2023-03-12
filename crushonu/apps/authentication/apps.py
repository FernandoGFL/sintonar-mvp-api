from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crushonu.apps.authentication'

    def ready(self):
        import crushonu.apps.authentication.signals

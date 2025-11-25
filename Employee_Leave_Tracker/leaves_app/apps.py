from django.apps import AppConfig


class LeavesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaves_app'


    def ready(self):
        import leaves_app.signals

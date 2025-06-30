from django.apps import AppConfig


class StudentConfig(AppConfig):
    name = 'apps.student'
    verbose_name = 'Priority'
    def ready(self):
        import apps.student.signals

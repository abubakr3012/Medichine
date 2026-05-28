from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
    name = 'appointments'
    verbose_name = 'Записи на приём'

    def ready(self):
        import appointments.signals  # noqa — подключаем сигналы

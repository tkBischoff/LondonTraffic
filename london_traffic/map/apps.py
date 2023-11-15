from django.apps import AppConfig
import logging


class MapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map'

    def ready(self):
        logging.info("Starting app")
        from map.scheduler import scheduler
        scheduler.start()

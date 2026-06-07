# Esto asegura que la app de Celery se cargue cada vez que Django arranca.
from .celery import app as celery_app

__all__ = ('celery_app',)
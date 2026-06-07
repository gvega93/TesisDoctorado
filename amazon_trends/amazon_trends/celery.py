import os
from celery import Celery

# Le decimos a Celery dónde están las configuraciones de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_trends.settings')

# Creamos la instancia de Celery llamándola 'amazon_trends'
app = Celery('amazon_trends')

# Cargamos las configuraciones desde settings.py usando el prefijo 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Le pedimos a Celery que busque tareas automáticamente en todas nuestras apps instaladas
app.autodiscover_tasks()
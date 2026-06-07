from django.urls import path
from .views import IngestaTendenciasAPIView

urlpatterns = [
    path('tendencias/ingestar/', IngestaTendenciasAPIView.as_view(), name='ingestar_tendencias'),
]

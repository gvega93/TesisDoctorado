from django.urls import path
from .views import IngestaTendenciasAPIView, tienda_publica, leer_articulo

urlpatterns = [
    # API Interna
    path('tendencias/ingestar/', IngestaTendenciasAPIView.as_view(), name='ingestar_tendencias'),
    
    # Rutas Públicas (El Frontend)
    path('tienda/<str:sub_id_afiliado>/', tienda_publica, name='tienda_publica'),
    path('tienda/<str:sub_id_afiliado>/<slug:slug>/', leer_articulo, name='leer_articulo'),
]

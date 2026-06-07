from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------------
    # API de Scrapers (Uso Interno de Máquinas)
    # -----------------------------------
    path('tendencias/ingestar/', views.IngestaTendenciasAPIView.as_view(), name='ingestar_tendencias'),
    
    # -----------------------------------
    # Frontend de la Tienda (Uso Público)
    # -----------------------------------
    
    # El Home con los 4 Cuadrantes (ej. /api/core/tienda/maria/)
    path('tienda/<str:username>/', views.ver_portal_usuario, name='tienda_home'),
    
    # La Vitrina por Categoría (ej. /api/core/tienda/maria/categoria/tecnologia/)
    path('tienda/<str:username>/categoria/<str:categoria>/', views.ver_categoria, name='ver_categoria'),
    
    # El Artículo Final / Página de Venta (ej. /api/core/tienda/maria/producto/zapatillas-running/)
    path('tienda/<str:username>/producto/<slug:slug>/', views.leer_articulo, name='leer_articulo'),
]
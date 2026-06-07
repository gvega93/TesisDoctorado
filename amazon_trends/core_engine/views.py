from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portal, Articulo, Tendencia

# ==========================================
# 1. VISTAS PÚBLICAS (SaaS Frontend)
# ==========================================

def ver_portal_usuario(request, username):
    """Vista del HOME: Muestra los 4 cuadrantes principales de la tienda del usuario."""
    portal = get_object_or_404(Portal, beneficiario__username=username)
    return render(request, 'core_engine/tienda_home.html', {'portal': portal})

def ver_categoria(request, username, categoria):
    """Vista de VITRINA: Muestra los productos de una categoría específica."""
    portal = get_object_or_404(Portal, beneficiario__username=username)
    articulos = portal.articulos.filter(categoria=categoria).order_by('-fecha_publicacion')
    
    # Mapeo de nombres para la UI (AQUÍ ACTUALIZAMOS MODA FEMENINA)
    nombres = {'tecnologia': 'Tecnología', 'hogar': 'Hogar', 'belleza': 'Belleza', 'moda_femenina': 'Moda Femenina'}
    nombre_cat = nombres.get(categoria, categoria.capitalize())
    
    return render(request, 'core_engine/categoria.html', {
        'portal': portal, 
        'articulos': articulos, 
        'categoria_nombre': nombre_cat
    })

def leer_articulo(request, username, slug):
    """Vista de VENTA: Muestra el artículo completo redactado por la IA."""
    articulo = get_object_or_404(Articulo, slug=slug, portal__beneficiario__username=username)
    
    # Sumar una visita para estadísticas de rentabilidad
    articulo.vistas += 1
    articulo.save(update_fields=['vistas'])
    
    return render(request, 'core_engine/leer_articulo.html', {
        'portal': articulo.portal,
        'articulo': articulo
    })

# ==========================================
# 2. VISTA DE LA API (Ingesta de Tendencias)
# ==========================================

class IngestaTendenciasAPIView(APIView):
    """Recibe datos masivos de los Scrapers (DrissionPage) y bloquea duplicados."""
    def post(self, request):
        tendencias_data = request.data.get('tendencias', [])
        if not tendencias_data or not isinstance(tendencias_data, list):
            return Response({"error": "Formato inválido. Se espera una lista en 'tendencias'."}, status=status.HTTP_400_BAD_REQUEST)

        nuevas_tendencias = []
        duplicados = 0

        for item in tendencias_data:
            if not Tendencia.objects.filter(termino_busqueda=item.get('termino_busqueda'), fuente=item.get('fuente')).exists():
                nuevas_tendencias.append(
                    Tendencia(
                        termino_busqueda=item.get('termino_busqueda'),
                        fuente=item.get('fuente'),
                        puntuacion_viral=item.get('puntuacion_viral', 0)
                    )
                )
            else:
                duplicados += 1

        if nuevas_tendencias:
            Tendencia.objects.bulk_create(nuevas_tendencias)

        return Response({
            "mensaje": "Ingesta completada",
            "nuevos_registros": len(nuevas_tendencias),
            "duplicados_omitidos": duplicados
        }, status=status.HTTP_201_CREATED)

# ==========================================
# 3. UTILIDAD (Redirección Automática UX)
# ==========================================
def redireccion_raiz(request):
    """
    Redirige automáticamente la raíz (127.0.0.1:8000) al primer portal creado.
    """
    portal = Portal.objects.first()
    if portal:
        return redirect('tienda_home', username=portal.beneficiario.username)
    return HttpResponse("<h3>Aún no hay portales. Por favor ejecuta test_final.py primero.</h3>")
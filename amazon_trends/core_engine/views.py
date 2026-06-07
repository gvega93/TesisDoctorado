from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tendencia
from .serializers import TendenciaSerializer

class IngestaTendenciasAPIView(APIView):
    def post(self, request):
        """
        Recibe un JSON con una lista de tendencias.
        """
        tendencias_data = request.data.get('tendencias', [])
        if not tendencias_data or not isinstance(tendencias_data, list):
            return Response({"error": "Formato inválido. Se espera una lista en 'tendencias'."}, status=status.HTTP_400_BAD_REQUEST)

        nuevas_tendencias = []
        duplicados = 0

        for item in tendencias_data:
            # Validamos si ya existe para no chocar con la restricción unique_together
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

        # Inserción masiva ultra-rápida (bulk_create)
        if nuevas_tendencias:
            Tendencia.objects.bulk_create(nuevas_tendencias)

        return Response({
            "mensaje": "Ingesta completada",
            "nuevos_registros": len(nuevas_tendencias),
            "duplicados_omitidos": duplicados
        }, status=status.HTTP_201_CREATED)


from django.shortcuts import render, get_object_or_404
from .models import Portal, Articulo

def tienda_publica(request, sub_id_afiliado):
    """Muestra el portal de un usuario específico usando su sub_id."""
    portal = get_object_or_404(Portal, sub_id_afiliado=sub_id_afiliado)
    articulos = portal.articulos.all().order_by('-fecha_publicacion')
    
    return render(request, 'core_engine/tienda.html', {
        'portal': portal,
        'articulos': articulos
    })

def leer_articulo(request, sub_id_afiliado, slug):
    """Muestra el artículo completo."""
    portal = get_object_or_404(Portal, sub_id_afiliado=sub_id_afiliado)
    articulo = get_object_or_404(Articulo, portal=portal, slug=slug)
    
    # Sumar una visita
    articulo.vistas += 1
    articulo.save(update_fields=['vistas'])
    
    return render(request, 'core_engine/articulo.html', {
        'portal': portal,
        'articulo': articulo
    })
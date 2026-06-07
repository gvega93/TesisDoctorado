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

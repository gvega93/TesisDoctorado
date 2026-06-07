import os
import sys
import django

# 1. Configurar el entorno de Django para ejecutar un script externo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_trends.settings')
django.setup()

# --- NUEVO: Autorizar 'testserver' en memoria para evitar el error de DisallowedHost ---
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

# 2. Importar herramientas de prueba después de inicializar Django
from rest_framework.test import APIClient
from core_engine.models import Tendencia

def ejecutar_prueba():
    print("\n--- INICIANDO PROTOCOLO DE VALIDACIÓN FASE 2 ---")
    
    # APIClient nos permite simular peticiones HTTP (POST, GET) a nuestra API local
    client = APIClient()
    url = '/api/core/tendencias/ingestar/'

    # Lote simulado de tendencias capturadas por nuestros agentes
    payload = {
        "tendencias": [
            {"termino_busqueda": "Mundial 2026", "fuente": "Google Trends", "puntuacion_viral": 99},
            {"termino_busqueda": "Zapatillas Inteligentes", "fuente": "TikTok", "puntuacion_viral": 85}
        ]
    }

    try:
        # Prueba 1: Inserción inicial (Camino feliz)
        response = client.post(url, payload, format='json')
        
        if response.status_code != 201:
            print(f"❌ ERROR CRÍTICO: La API devolvió un código de error {response.status_code}")
            print(f"Detalle: {response.content.decode('utf-8')}")
            sys.exit(1)

        data = response.json()
        assert data['nuevos_registros'] == 2, "La API no reportó las 2 inserciones."
        print("✔️ Ingesta masiva inicial a través de la API exitosa (Código 201).")

        # Prueba 2: Validación de protección contra duplicados
        # Volvemos a enviar exactamente el mismo lote de datos
        response_dup = client.post(url, payload, format='json')
        data_dup = response_dup.json()
        
        assert data_dup['nuevos_registros'] == 0, "La API insertó registros que ya existían."
        assert data_dup['duplicados_omitidos'] == 2, "La API no contó correctamente los duplicados omitidos."
        print("✔️ Protección contra duplicados (unique_together) operativa. No se repite información.")

        # Prueba 3: Consistencia en Base de Datos
        total = Tendencia.objects.count()
        assert total == 2, f"Hay {total} registros en BD, deberían ser exactamente 2."
        print("✔️ Consistencia directa en la base de datos confirmada.")

        print("\n✅ FASE 2 APROBADA 100%: API de Ingesta masiva y filtro de repetidos validados.\n")

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO EN LA PRUEBA: {str(e)}\n")
    
    finally:
        # Paso final: Limpiar la tabla de tendencias para dejar la BD inmaculada
        Tendencia.objects.all().delete()
        print("Limpieza del entorno de pruebas completada.")

if __name__ == "__main__":
    ejecutar_prueba()
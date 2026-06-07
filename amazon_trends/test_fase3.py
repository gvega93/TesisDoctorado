import os
import django

# 1. Configurar el entorno de Django para ejecutar un script externo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_trends.settings')
django.setup()

# 2. Importar nuestra tarea asíncrona
from core_engine.tasks import procesar_tendencia_ia

def ejecutar_prueba():
    print("\n--- INICIANDO PROTOCOLO DE VALIDACIÓN FASE 3 ---")
    print("Enviando orden a los agentes en segundo plano...")

    # .delay() toma la tarea y la envía a la cola de Redis. 
    # El código NO se detiene a esperar los 15 segundos que tarda el agente.
    resultado = procesar_tendencia_ia.delay("Zapatillas Running", "https://portaltesis.com")

    print(f"✔️ Orden enviada a la cola. ID de la tarea: {resultado.id}")
    print("✔️ Tu servidor web (esta terminal) está libre de inmediato.")
    print("⏳ Revisa tu OTRA terminal (la de Celery) para ver al agente trabajando.\n")

if __name__ == "__main__":
    ejecutar_prueba()
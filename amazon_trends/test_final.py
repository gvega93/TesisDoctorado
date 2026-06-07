import os
import django
from decimal import Decimal

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_trends.settings')
django.setup()

from core_engine.models import Beneficiario, Portal, BilleteraUsuario, Tendencia
from core_engine.tasks import procesar_tendencia_ia

def ejecutar_prueba_final():
    print("\n--- 🚀 INICIANDO PRUEBA DE EXTREMO A EXTREMO (END-TO-END) ---")
    
    # 1. Crear un usuario "Beneficiario" de prueba (Población vulnerable)
    user, created = Beneficiario.objects.get_or_create(
        username='maria_emprende',
        defaults={'telefono_nequi': '3009876543'}
    )
    if created:
        user.set_password('password123')
        user.save()
        print("✔️ Beneficiario 'maria_emprende' creado.")

    # 2. Darle una billetera con saldo para que la IA funcione
    BilleteraUsuario.objects.get_or_create(
        beneficiario=user,
        defaults={'saldo_consumo_ia': Decimal('10.00')}
    )

    # 3. Crear su Portal Web Automatizado
    sub_id = 'maria-tech-01'
    portal, p_created = Portal.objects.get_or_create(
        beneficiario=user,
        dominio='https://marias-tech.com',
        defaults={
            'nombre_sitio': 'Tecnología para Todos',
            'sub_id_afiliado': sub_id,
            'nicho': 'Tecnología y Gadgets',
            'estado': 'activo'
        }
    )
    if p_created:
        print(f"✔️ Portal '{portal.nombre_sitio}' creado.")

    # 4. Simular que el Scraper encontró una tendencia
    tendencia, t_created = Tendencia.objects.get_or_create(
        termino_busqueda='Auriculares Inalámbricos con Cancelación de Ruido',
        fuente='Prueba Manual',
        defaults={'puntuacion_viral': 95}
    )

    print(f"\n📡 Enviando la orden a los agentes para investigar: '{tendencia.termino_busqueda}'...")
    
    # 5. Enviar la orden a Celery pasando los IDs reales de la base de datos
    resultado = procesar_tendencia_ia.delay(tendencia.id, portal.id, "Español")

    print(f"✔️ Orden enviada a Celery (ID: {resultado.id})")
    print(f"🌐 Cuando el agente termine, tu página web estará disponible en:")
    print(f"   --> http://127.0.0.1:8000/api/core/tienda/{sub_id}/")
    print("\n⏳ Ve a la terminal de Celery para ver a los agentes escribir...")

if __name__ == "__main__":
    ejecutar_prueba_final()
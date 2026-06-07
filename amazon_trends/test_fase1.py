import os
import sys
import django
from decimal import Decimal # Importamos la librería matemática de alta precisión

# 1. Configurar el entorno de Django para ejecutar un script externo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_trends.settings')
django.setup()

# 2. Importar los modelos después de inicializar Django
from core_engine.models import Beneficiario, Portal, BilleteraUsuario
from django.db import transaction

def ejecutar_prueba():
    print("\n--- INICIANDO PROTOCOLO DE VALIDACIÓN FASE 1 ---")
    try:
        # Paso 1: Creación de entidades respetando integridad referencial
        user = Beneficiario.objects.create_user(
            username='usuario_tesis',
            password='password123',
            telefono_nequi='3001234567'
        )
        
        wallet = BilleteraUsuario.objects.create(
            beneficiario=user,
            # Le damos $5 USD de recarga inicial para IA usando Decimal
            saldo_consumo_ia=Decimal('5.00')  
        )
        
        portal = Portal.objects.create(
            beneficiario=user,
            nombre_sitio='Portal Tesis',
            dominio='https://portaltesis.com',
            sub_id_afiliado='tesis-nequi-01',
            nicho='Educación'
        )
        print("✔️ Entidades creadas (Beneficiario, Billetera, Portal).")

        # Paso 2: Validación de abono de ganancias (Afiliados Amazon)
        wallet.abonar_ganancias(Decimal('12.50')) # El portal generó $12.50
        assert wallet.ganancias_acumuladas == Decimal('12.50'), "Error matemático en abono."
        print("✔️ Abono de ganancias atómico verificado.")

        # Paso 3: Validación de consumo IA (Camino feliz)
        # El agente gasta $2.00 generando artículos
        wallet.descontar_consumo_ia(Decimal('2.00'))
        assert wallet.saldo_consumo_ia == Decimal('3.00'), "Error matemático en descuento."
        print("✔️ Cobro de consumo de Agentes IA verificado.")

        # Paso 4: Validación de seguridad (Camino de error intencional)
        # El agente intenta gastar $10.00, pero solo quedan $3.00
        try:
            wallet.descontar_consumo_ia(Decimal('10.00'))
            print("❌ ERROR CRÍTICO: El sistema permitió gastar saldo inexistente.")
            sys.exit(1)
        except ValueError as e:
            print(f"✔️ Bloqueo de seguridad financiero activado correctamente: '{str(e)}'")

        print("\n✅ FASE 1 APROBADA 100%: Arquitectura relacional y control financiero superados.\n")

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO EN LA PRUEBA: {str(e)}\n")
    
    finally:
        # Paso 5: Limpieza de la base de datos
        if 'user' in locals():
            user.delete()
            print("Limpieza del entorno de pruebas completada.")

if __name__ == "__main__":
    ejecutar_prueba()
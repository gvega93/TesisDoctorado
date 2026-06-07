import time
import requests
from DrissionPage import ChromiumPage

def obtener_tendencias_amazon(page):
    print("🌐 [AMAZON] Buscando tendencias consolidadas (Best Sellers)...")
    url = 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/'
    page.get(url)
    time.sleep(4)
    
    tendencias = []
    productos = page.eles('x://div[contains(@class, "zg-grid-general-faceout")]')
    if not productos:
        productos = page.eles('.p13n-sc-uncoverable-faceout')

    for i, item in enumerate(productos[:5]):
        try:
            texto_crudo = item.text
            lineas = texto_crudo.split('\n')
            if lineas:
                titulo = max(lineas, key=len)
                tendencias.append({
                    "termino_busqueda": titulo[:150],
                    "fuente": "Amazon Best Sellers",
                    "puntuacion_viral": 100 - i
                })
        except Exception as e:
            pass
            
    print(f"   -> {len(tendencias)} tendencias extraídas de Amazon.")
    return tendencias

def obtener_tendencias_aliexpress(page):
    print("🌐 [ALIEXPRESS] Buscando tendencias emergentes de manufactura Asiática...")
    url = 'https://www.aliexpress.com/'
    page.get(url)
    # Simulamos el tiempo de espera y el scroll humano
    time.sleep(3)
    
    tendencias = []
    # Aquí iría el XPath específico para los SuperDeals o Top Rankings de AliExpress.
    # A modo de demostración para la API, inyectamos una tendencia detectada en Asia:
    tendencias.append({
        "termino_busqueda": "Smartwatch Monitor Glucosa No Invasivo", 
        "fuente": "AliExpress SuperDeals",
        "puntuacion_viral": 98 # Alta puntuación por ser tendencia temprana
    })
    
    print(f"   -> {len(tendencias)} tendencias tempranas extraídas de AliExpress.")
    return tendencias

def enviar_a_nuestra_api(tendencias):
    if not tendencias:
        print("⚠️ No hay tendencias para enviar.")
        return

    url_api = "http://127.0.0.1:8000/api/core/tendencias/ingestar/"
    payload = {"tendencias": tendencias}
    
    print(f"\n📡 Enviando {len(tendencias)} tendencias combinadas a nuestra API local...")
    try:
        response = requests.post(url_api, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ ¡ÉXITO! Base de datos actualizada:")
            print(f"   - Nuevas tendencias globales guardadas: {data['nuevos_registros']}")
            print(f"   - Duplicados bloqueados: {data['duplicados_omitidos']}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Enciende el servidor Django en otra terminal (python manage.py runserver)")

if __name__ == '__main__':
    print("🚀 INICIANDO RECOLECCIÓN MULTI-MERCADO...")
    # Abrimos un solo navegador para optimizar memoria
    navegador = ChromiumPage()
    
    todas_las_tendencias = []
    
    try:
        # 1. Escaneamos Amazon (Mercado Maduro)
        tendencias_amz = obtener_tendencias_amazon(navegador)
        todas_las_tendencias.extend(tendencias_amz)
        
        # 2. Escaneamos AliExpress (Mercado Emergente / Proveedores)
        tendencias_ali = obtener_tendencias_aliexpress(navegador)
        todas_las_tendencias.extend(tendencias_ali)
        
        # 3. Podrías agregar funciones para TikTok, Temu, Kickstarter, etc.
        
    finally:
        # Cerramos el navegador sin importar qué pase
        navegador.quit()
        
    # Enviamos el paquete masivo con datos de todo el mundo a nuestro "Cerebro"
    enviar_a_nuestra_api(todas_las_tendencias)
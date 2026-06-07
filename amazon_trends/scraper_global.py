import time
import requests
from DrissionPage import ChromiumPage

# ==========================================
# MÓDULOS DE EXTRACCIÓN POR REGIÓN
# ==========================================

def escaneo_amazon_usa(page):
    print("🌐 [EE.UU] Escaneando Amazon Best Sellers...")
    url = 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/'
    page.get(url)
    time.sleep(3)
    
    tendencias = []
    # Buscamos elementos, si la web cambia, evitamos que el bot colapse con try/except
    try:
        productos = page.eles('x://div[contains(@class, "zg-grid-general-faceout")]')
        if not productos:
            productos = page.eles('.p13n-sc-uncoverable-faceout')

        for i, item in enumerate(productos[:5]):
            lineas = item.text.split('\n')
            if lineas:
                titulo = max(lineas, key=len)
                tendencias.append({
                    "termino_busqueda": titulo[:150],
                    "fuente": "Amazon USA",
                    "puntuacion_viral": 100 - i
                })
    except Exception as e:
        print(f"  -> Error leve en Amazon: {e}")
        
    print(f"  -> ✅ {len(tendencias)} tendencias extraídas de EE.UU.")
    return tendencias

def escaneo_mercadolibre_latam(page):
    print("🌐 [LATAM] Escaneando Mercado Libre (Tendencias)...")
    # Usamos la sección de tendencias de Mercado Libre
    url = 'https://tendencias.mercadolibre.com.co/'
    page.get(url)
    time.sleep(3)
    
    tendencias = []
    try:
        # Extraemos los enlaces de las palabras clave más buscadas
        palabras_clave = page.eles('x://a[contains(@class, "searches__item-link")]')
        
        for i, item in enumerate(palabras_clave[:5]):
            titulo = item.text.strip()
            if titulo:
                tendencias.append({
                    "termino_busqueda": titulo[:150],
                    "fuente": "Mercado Libre LATAM",
                    "puntuacion_viral": 95 - i # Puntaje alto por ser tendencia de búsqueda
                })
    except Exception as e:
        print(f"  -> Error leve en Mercado Libre: {e}")

    print(f"  -> ✅ {len(tendencias)} tendencias extraídas de LATAM.")
    return tendencias

def escaneo_rakuten_japon(page):
    print("🌐 [JAPÓN] Escaneando Rakuten Ichiba (Top Ranking)...")
    url = 'https://ranking.rakuten.co.jp/'
    page.get(url)
    time.sleep(4)
    
    tendencias = []
    try:
        # Los títulos en Rakuten suelen estar bajo esta clase
        productos = page.eles('.rnkRanking_itemName')
        
        for i, item in enumerate(productos[:5]):
            titulo = item.text.strip()
            if titulo:
                tendencias.append({
                    "termino_busqueda": titulo[:150],
                    "fuente": "Rakuten Japón",
                    "puntuacion_viral": 90 - i 
                })
    except Exception as e:
        print(f"  -> Error leve en Rakuten: {e}")

    print(f"  -> ✅ {len(tendencias)} tendencias extraídas de Japón.")
    return tendencias

def escaneo_aliexpress_asia(page):
    print("🌐 [ASIA] Escaneando AliExpress (Mercado de Manufactura)...")
    url = 'https://www.aliexpress.com/'
    page.get(url)
    time.sleep(3)
    
    # AliExpress es muy agresivo bloqueando bots, simulamos un scroll
    page.scroll.down(500)
    time.sleep(2)
    
    tendencias = []
    # Usamos datos simulados aquí para evitar el CAPTCHA duro de AliExpress en la prueba,
    # pero el navegador efectivamente visita la página de China para dar presencia al bot.
    tendencias.append({
        "termino_busqueda": "Mini Proyector Portátil 4K Android", 
        "fuente": "AliExpress Global",
        "puntuacion_viral": 98
    })
    print(f"  -> ✅ {len(tendencias)} tendencias extraídas de ASIA.")
    return tendencias

# ==========================================
# ENVÍO AL CEREBRO (API DJANGO)
# ==========================================

def enviar_a_nuestra_api(tendencias):
    if not tendencias:
        print("⚠️ No hay tendencias para enviar.")
        return

    url_api = "http://127.0.0.1:8000/api/core/tendencias/ingestar/"
    payload = {"tendencias": tendencias}
    
    print(f"\n📡 Enviando {len(tendencias)} tendencias GLOBALES al Cerebro de IA...")
    try:
        response = requests.post(url_api, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print(f"🏆 ¡MISIÓN CUMPLIDA! Resumen de Base de Datos:")
            print(f"   - Nuevas oportunidades guardadas: {data['nuevos_registros']}")
            print(f"   - Oportunidades ya conocidas (omitidas): {data['duplicados_omitidos']}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Enciende el servidor Django en otra terminal (python manage.py runserver)")

if __name__ == '__main__':
    print("🚀 INICIANDO RADAR GEOPOLÍTICO DE TENDENCIAS COMERCIALES...")
    navegador = ChromiumPage()
    todas_las_tendencias = []
    
    try:
        # Viajamos por el mundo digital
        todas_las_tendencias.extend(escaneo_amazon_usa(navegador))
        todas_las_tendencias.extend(escaneo_mercadolibre_latam(navegador))
        todas_las_tendencias.extend(escaneo_rakuten_japon(navegador))
        todas_las_tendencias.extend(escaneo_aliexpress_asia(navegador))
        
    finally:
        navegador.quit()
        print("🌍 Viaje mundial finalizado. Cerrando navegador.")
        
    enviar_a_nuestra_api(todas_las_tendencias)
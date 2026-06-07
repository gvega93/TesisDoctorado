from celery import shared_task
from .agentes import ejecutar_equipo_redaccion

@shared_task
def procesar_tendencia_ia(tendencia_nombre, portal_dominio, nicho="Tecnología"):
    """
    Tarea asíncrona que lanza el equipo de CrewAI.
    """
    print(f"🤖 [CELERY]: Iniciando equipo CrewAI para el tema '{tendencia_nombre}'...")
    
    try:
        # Llamamos a nuestro orquestador
        articulo_generado = ejecutar_equipo_redaccion(tema=tendencia_nombre, nicho=nicho)
        
        print(f"✅ [CELERY]: Artículo generado con éxito. Longitud: {len(articulo_generado)} caracteres.")
        print("--- EXTRACTO DEL ARTÍCULO ---")
        print(articulo_generado[:300] + "...") # Imprimimos los primeros 300 caracteres
        
        # Aquí en el futuro agregaremos el código para enviar este texto a WordPress
        
        return f"Éxito: Artículo sobre {tendencia_nombre} generado."
        
    except Exception as e:
        print(f"❌ [CELERY ERROR CRÍTICO]: Fallo en CrewAI: {str(e)}")
        return f"Error: {str(e)}"


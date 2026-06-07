from celery import shared_task
import time

@shared_task
def procesar_tendencia_ia(tendencia_nombre, portal_dominio):
    """
    Esta función simula el trabajo pesado de un Agente IA (CrewAI).
    En lugar de bloquear el servidor web, se ejecutará en segundo plano.
    """
    print(f"🤖 [AGENTE INICIADO]: Investigando la tendencia '{tendencia_nombre}' en la web...")
    
    # Simulamos que la IA tarda 10 segundos leyendo, resumiendo y escribiendo
    time.sleep(10) 
    
    print(f"✍️ [AGENTE TRABAJANDO]: Redactando el artículo para {portal_dominio}...")
    
    # Simulamos que tarda 5 segundos más publicando en WordPress
    time.sleep(5)
    
    print(f"✅ [AGENTE TERMINÓ]: Artículo sobre '{tendencia_nombre}' publicado con éxito en {portal_dominio}!")
    
    return f"Éxito: {tendencia_nombre} procesado."

from celery import shared_task
from .agentes import ejecutar_equipo_redaccion
from .models import Portal, Articulo, Tendencia

@shared_task
def procesar_tendencia_ia(tendencia_id, portal_id, idioma="Español"):
    """
    1. Lee la tendencia y el portal de la base de datos.
    2. Envía a la Agencia IA a redactar.
    3. Guarda el artículo publicado en el portal.
    """
    try:
        # 1. Traer los datos reales de la BD
        tendencia = Tendencia.objects.get(id=tendencia_id)
        portal = Portal.objects.get(id=portal_id)
        
        print(f"🤖 [CELERY]: Agencia IA investigando '{tendencia.termino_busqueda}' para {portal.dominio} en {idioma}...")
        
        # 2. Llamar a los agentes
        contenido_generado = ejecutar_equipo_redaccion(tema=tendencia.termino_busqueda, nicho=portal.nicho, idioma=idioma)
        
        # 3. Guardar en la base de datos (El título lo extraemos dinámicamente o le ponemos uno genérico para la URL)
        titulo_seo = f"Todo sobre {tendencia.termino_busqueda}"
        
        Articulo.objects.create(
            portal=portal,
            tendencia=tendencia,
            titulo=titulo_seo,
            contenido_html=contenido_generado,
            idioma=idioma
        )
        
        # Marcamos la tendencia como procesada
        tendencia.procesado = True
        tendencia.save()
        
        print(f"✅ [CELERY]: Artículo publicado en el portal de {portal.beneficiario.username}!")
        return True
        
    except Exception as e:
        print(f"❌ [CELERY ERROR]: {str(e)}")
        return False

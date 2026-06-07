import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv, find_dotenv

# Cargamos las variables del .env usando find_dotenv() como radar
load_dotenv(find_dotenv())

# Validamos que la clave de API exista
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key or openai_api_key == "sk-tu-clave-aqui-...":
    raise ValueError("Falta configurar una OPENAI_API_KEY válida en el archivo .env")

# Configuraciones de seguridad para evitar bloqueos en Windows
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
os.environ["MAX_RETRIES"] = "2"

def ejecutar_equipo_redaccion(tema: str, nicho: str, idioma: str = "Español") -> str:
    """
    Orquesta una AGENCIA DE MARKETING de IA completa y MULTILENGUAJE.
    """
    
    # ==========================================
    # 1. DEFINICIÓN DEL EQUIPO (AGENTES)
    # ==========================================
    
    investigador = Agent(
        role='Analista de Mercado Global',
        goal=f'Descubrir los productos más rentables, pros y contras sobre: {tema}',
        backstory=(
            "Eres un experto analista de e-commerce. Conoces las tendencias actuales "
            f"del nicho de {nicho}. Sabes qué características técnicas buscan los compradores."
        ),
        verbose=True,
        allow_delegation=False
    )

    estratega_marketing = Agent(
        role='Director de Marketing Digital',
        goal=f'Definir el ángulo de venta y los gatillos psicológicos para vender {tema} a una audiencia que habla {idioma}',
        backstory=(
            "Eres un estratega de marketing de élite que ha facturado millones en afiliación. "
            "Sabes cómo conectar un producto con las emociones del usuario. Utilizas "
            "gatillos como la prueba social, la urgencia y el miedo a perderse la oferta (FOMO). "
            f"Es VITAL que toda tu estrategia esté adaptada a la cultura del idioma {idioma}."
        ),
        verbose=True,
        allow_delegation=False
    )

    redactor_copywriter = Agent(
        role='Copywriter de Conversión (SEO)',
        goal=f'Escribir un artículo HTML altamente persuasivo en {idioma} basado en la estrategia.',
        backstory=(
            "Eres un maestro de las palabras. Escribes textos que atrapan al lector desde "
            f"el primer párrafo. Redactas de forma nativa e impecable en {idioma}. "
            "Sabes integrar enlaces de afiliados de forma natural, usando llamados a la acción (CTAs) irresistibles."
        ),
        verbose=True,
        allow_delegation=False
    )

    editor_jefe = Agent(
        role='Editor en Jefe y Validador de Calidad',
        goal=f'Auditar el artículo final, asegurar que esté en perfecto {idioma}, cumpla la estrategia y entregarlo en HTML puro.',
        backstory=(
            "Eres el líder del equipo y el filtro final. Eres implacable con la calidad. "
            f"Revisas que la gramática y el tono en {idioma} fluyan perfectamente, que el HTML sea impecable y "
            "que el potencial de monetización sea máximo. Si detectas palabras en otro idioma, lo corriges."
        ),
        verbose=True,
        allow_delegation=False
    )
    
    # NOTA FUTURA: Aquí añadiremos el Agente 'Influencer_Social_Media' 
    # que tomará el texto del Editor Jefe y creará hilos de Twitter y Guiones de TikTok.

    # ==========================================
    # 2. DEFINICIÓN DE LAS TAREAS (WORKFLOW)
    # ==========================================
    
    tarea_investigacion = Task(
        description=f'Extrae datos duros, top de productos y características técnicas sobre "{tema}".',
        expected_output='Informe técnico de productos, pros y contras.',
        agent=investigador
    )

    tarea_estrategia = Task(
        description=(
            f'Revisa el informe del investigador sobre "{tema}". '
            f'Diseña una estrategia de 3 puntos adaptada al mercado de idioma {idioma}: '
            '1) A quién le vendemos (Target), 2) Qué problema emocional le resolvemos, 3) Qué CTAs usar.'
        ),
        expected_output='Documento de estrategia de marketing detallado.',
        agent=estratega_marketing
    )

    tarea_redaccion = Task(
        description=(
            f'Usa el informe técnico y la estrategia para redactar el artículo de ventas en {idioma}. '
            'Debe tener un título H1 atractivo y subtítulos H2. '
            'Integra los productos de forma natural para que el lector quiera comprarlos.'
        ),
        expected_output='Borrador completo del artículo de ventas.',
        agent=redactor_copywriter
    )

    tarea_auditoria_final = Task(
        description=(
            f'Toma el borrador del copywriter. Valida lo siguiente: '
            '1. ¿El título es magnético? '
            '2. ¿Los gatillos mentales están presentes? '
            f'3. ¿El texto está escrito 100% en {idioma} natural? '
            'Haz las correcciones necesarias y entrega la versión definitiva EXCLUSIVAMENTE en formato HTML '
            '(Usa etiquetas <h1>, <h2>, <p>, <strong> y <ul>). No incluyas etiquetas <body>, <html> o delimitadores markdown (```html), SOLO el contenido HTML puro.'
        ),
        expected_output=f'Artículo pulido, persuasivo, escrito en {idioma} y formateado en HTML puro, listo para la base de datos.',
        agent=editor_jefe
    )

    # ==========================================
    # 3. ORQUESTACIÓN DEL EQUIPO
    # ==========================================
    
    agencia_ia = Crew(
        agents=[investigador, estratega_marketing, redactor_copywriter, editor_jefe],
        tasks=[tarea_investigacion, tarea_estrategia, tarea_redaccion, tarea_auditoria_final],
        # Proceso secuencial: Cada uno entrega su trabajo al siguiente
        process=Process.sequential, 
        verbose=True
    )

    resultado_final = agencia_ia.kickoff()
    
    return str(resultado_final)
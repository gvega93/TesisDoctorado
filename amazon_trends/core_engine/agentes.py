import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

# Validamos que la clave de API exista
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key or openai_api_key == "sk-tu-clave-aqui-...":
    raise ValueError("Falta configurar una OPENAI_API_KEY válida en el archivo .env")

# --- LA SOLUCIÓN Y PROTECCIÓN ---
# Forzamos las variables en el sistema operativo para que CrewAI/LiteLLM las tome sí o sí.
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
# Evitamos que se quede "congelado" intentando infinitamente si hay error de saldo
os.environ["MAX_RETRIES"] = "2"

def ejecutar_equipo_redaccion(tema: str, nicho: str) -> str:
    """
    Orquesta un equipo de agentes para investigar y redactar un artículo SEO.
    """
    
    # 1. Definir los Agentes (Ya no necesitan el parámetro llm explícito)
    investigador = Agent(
        role='Investigador de Tendencias de Mercado',
        goal=f'Descubrir los productos más rentables y populares relacionados con: {tema}',
        backstory=(
            "Eres un experto analista de e-commerce y tendencias. "
            "Sabes exactamente qué características buscan los consumidores y qué productos "
            "se venden mejor en el nicho de {nicho}."
        ),
        verbose=True,
        allow_delegation=False
    )

    redactor_seo = Agent(
        role='Redactor SEO para Afiliados',
        goal=f'Escribir un artículo persuasivo y optimizado para SEO sobre {tema} que genere ventas.',
        backstory=(
            "Eres un copywriter experto en marketing de afiliados. "
            "Sabes cómo estructurar un artículo para mantener al lector enganchado "
            "y persuadirlo sutilmente para que haga clic en los enlaces de compra."
        ),
        verbose=True,
        allow_delegation=False
    )

    # 2. Definir las Tareas
    tarea_investigacion = Task(
        description=(
            f'Investiga a fondo el tema "{tema}" en el nicho de {nicho}. '
            'Identifica los 3 principales productos recomendados, sus ventajas y desventajas. '
            'Redacta un informe detallado con estos hallazgos.'
        ),
        expected_output='Un informe estructurado con 3 productos, pros, contras y razones de popularidad.',
        agent=investigador
    )

    tarea_redaccion = Task(
        description=(
            f'Usando el informe del investigador, redacta un artículo de blog sobre "{tema}". '
            'El artículo debe tener un título atractivo (H1), subtítulos (H2), e incluir '
            'llamados a la acción (CTA) para comprar los productos. Formato Markdown.'
        ),
        expected_output='Un artículo completo en formato Markdown listo para publicar.',
        agent=redactor_seo
    )

    # 3. Ensamblar el Equipo (Crew)
    equipo = Crew(
        agents=[investigador, redactor_seo],
        tasks=[tarea_investigacion, tarea_redaccion],
        process=Process.sequential, 
        verbose=True
    )

    # 4. Iniciar el trabajo
    resultado_final = equipo.kickoff()
    
    return str(resultado_final)
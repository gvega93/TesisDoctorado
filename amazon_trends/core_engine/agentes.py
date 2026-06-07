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
    Orquesta una AGENCIA DE MARKETING de IA completa, MULTILENGUAJE y con UX/UI (Tailwind).
    """
    
    # ==========================================
    # 1. DEFINICIÓN DEL EQUIPO (AGENTES)
    # ==========================================
    
    investigador = Agent(
        role='Analista de Mercado Global y Precios',
        goal=f'Descubrir los productos más rentables, estimar precios locales vs internacionales, pros y contras sobre: {tema}',
        backstory=(
            "Eres un experto analista de e-commerce. Conoces las tendencias actuales "
            f"del nicho de {nicho}. Sabes qué características técnicas buscan los compradores "
            "y eres experto en encontrar la diferencia de precio entre tiendas locales y Amazon."
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
        goal=f'Escribir el cuerpo del artículo altamente persuasivo en {idioma} basado en la estrategia.',
        backstory=(
            "Eres un maestro de las palabras. Escribes textos que atrapan al lector desde "
            f"el primer párrafo. Redactas de forma nativa e impecable en {idioma}. "
            "Sabes integrar la necesidad del producto de forma natural para preparar la venta."
        ),
        verbose=True,
        allow_delegation=False
    )

    editor_jefe = Agent(
        role='Editor en Jefe y Desarrollador UI/UX',
        goal=f'Auditar el idioma {idioma}, formatear en HTML con Tailwind CSS, y agregar tablas de precios e imágenes.',
        backstory=(
            "Eres el líder del equipo y un genio del diseño web. Eres implacable con la calidad. "
            f"Revisas que la gramática en {idioma} fluya perfectamente. "
            "Transformas el texto plano en una obra de arte HTML usando clases de Tailwind CSS. "
            "Tus artículos SIEMPRE incluyen un cuadro destacado comparando precios y botones grandes de compra."
        ),
        verbose=True,
        allow_delegation=False
    )

    # ==========================================
    # 2. DEFINICIÓN DE LAS TAREAS (WORKFLOW)
    # ==========================================
    
    tarea_investigacion = Task(
        description=f'Extrae datos duros, top de productos, estimación de precios y características sobre "{tema}".',
        expected_output='Informe técnico de productos, pros, contras y precios estimados.',
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
            'El texto debe ser persuasivo, fluido y generar deseo de compra. '
            'Entrega el texto en párrafos claros.'
        ),
        expected_output='Borrador completo del artículo de ventas en texto plano.',
        agent=redactor_copywriter
    )

    tarea_auditoria_final = Task(
        description=(
            f'Toma el borrador del copywriter. Valida que esté en {idioma} perfecto. '
            'Luego, conviértelo EXCLUSIVAMENTE en HTML puro (SIN <html>, SIN <body>, SIN ```html). '
            'DEBE incluir obligatoriamente: \n'
            '1. Un título principal atractivo <h1> con clases Tailwind (ej. text-3xl font-bold text-gray-900 mb-6).\n'
            '2. Una imagen ilustrativa justo después del título usando: <img src="https://loremflickr.com/800/500/tecnologia" class="w-full rounded-2xl shadow-lg mb-8">\n'
            '3. Una tabla o cuadro comparativo de precios (Local vs Amazon) usando Tailwind (ej. bg-gray-50 p-6 rounded-xl border border-gray-200).\n'
            '4. Un botón de compra vistoso que incite a hacer clic (ej. bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition).'
        ),
        expected_output=f'Artículo pulido en {idioma}, estructurado con Tailwind CSS, imágenes y tabla de precios, listo para Django.',
        agent=editor_jefe
    )

    # ==========================================
    # 3. ORQUESTACIÓN DEL EQUIPO
    # ==========================================
    
    agencia_ia = Crew(
        agents=[investigador, estratega_marketing, redactor_copywriter, editor_jefe],
        tasks=[tarea_investigacion, tarea_estrategia, tarea_redaccion, tarea_auditoria_final],
        process=Process.sequential, 
        verbose=True
    )

    resultado_final = agencia_ia.kickoff()
    
    return str(resultado_final)
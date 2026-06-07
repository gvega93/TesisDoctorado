import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Cargar la clave del .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print(f"Llave detectada: {api_key[:10]}... (oculta por seguridad)")

try:
    print("Conectando con OpenAI...")
    llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=api_key, max_retries=0)
    respuesta = llm.invoke("Hola, responde solo con la palabra 'Conectado'.")
    print(f"\n✅ ¡ÉXITO! OpenAI respondió: {respuesta.content}")
except Exception as e:
    print(f"\n❌ ERROR DE OPENAI: {str(e)}")
    if "insufficient_quota" in str(e) or "429" in str(e):
        print("-> DIAGNÓSTICO: Tu clave es válida, pero tu cuenta NO TIENE SALDO.")
        print("-> SOLUCIÓN: Debes ir a platform.openai.com/account/billing y recargar $5 USD.")
    elif "Incorrect API key" in str(e) or "401" in str(e):
        print("-> DIAGNÓSTICO: La clave de API está mal escrita o tiene espacios extra.")
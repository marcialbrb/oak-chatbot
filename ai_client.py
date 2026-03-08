import requests
from config import API_KEY, MODEL, SYSTEM_MESSAGE


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def _completar(mensajes: list[dict]) -> str:
    """Envía mensajes al modelo y devuelve el texto de respuesta."""
    data = {"model": MODEL, "messages": mensajes}
    try:
        response = requests.post(OPENROUTER_URL, json=data, headers=HEADERS)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Error: respuesta inesperada de la API:", response.json())
        return "Ocurrió un error al procesar la respuesta."
    except requests.RequestException as e:
        print(f"Error en la petición a la API: {e}")
        return f"Error de conexión: {e}"


def obtener_respuesta(pregunta: str, historial: list[dict]) -> str:
    """Genera una respuesta del Profesor Oak dado el historial de conversación."""
    
    # Asegurarse de que el historial alterna user/assistant correctamente
    historial_limpio = []
    ultimo_rol = None
    for mensaje in historial:
        if mensaje["role"] != ultimo_rol:
            historial_limpio.append(mensaje)
            ultimo_rol = mensaje["role"]
    
    mensajes = [SYSTEM_MESSAGE, *historial_limpio, {"role": "user", "content": pregunta}]
    return _completar(mensajes)


def resumir_respuesta(respuesta: str) -> str:
    """Resume un texto a menos de 1900 caracteres usando el modelo."""
    mensajes = [
        {"role": "system", "content": "Eres un experto en resumir textos."},
        {
            "role": "user",
            "content": f"Resumí el siguiente texto a menos de 1900 caracteres:\n\n{respuesta}",
        },
    ]
    return _completar(mensajes)

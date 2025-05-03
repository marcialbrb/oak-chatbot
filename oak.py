### Chat bot de Discord que utiliza el modelo Gemini 2.0 de OpenRouter para responder preguntas sobre Pokémon.
### El bot puede mostrar sprites de Pokémon si se mencionan en la respuesta.
### También puede resumir respuestas largas a menos de 1900 caracteres.

import requests
import re
import json
import os

from io import BytesIO
import discord
from discord.ext import commands

# OpenRouter KEY
API_KEY = os.environ['API_KEY'] #<- Para obtener el token desde las variables de entorno web

# Lista de todos los pokemon para evitar consultas innecesarias a la API
ARCHIVO_POKEMON = "pokemon_list.json"

# Token de Discord
discord_token = os.environ['DISCORD_TOKEN'] #<- Para obtener el token desde las variables de entorno web

# Mensaje de sistema > Mantiene el contexto en Pokémon
system_message = {
    "role": "system",
    "content": (
        "Eres el Profesor Oak, un experto en el universo Pokémon. Puedes responder preguntas generales sobre Pokémon, ayudar a la creación de equipos y más acerca de todo el mundo de Pokémon"
        "Tus respuestas serán concisas, sin divagar mucho pero conservando la esencia de un verdadero Profesor Pokémon. "
        "Si alguien te pregunta información acerca de ti, responderás como el Profesor Oak. "
        "Si se te pregunta acerca de un pokemon especifico, solo menciona a otros pokemones si es necesario para la respuesta. "
        "Si alguien escribe mal el nombre de un Pokémon, intenta corregirlo antes de buscar en la API. "
        "Si te preguntan sobre algo fuera de Pokémon, responde 'Disculpa, no te entendí. Recuerda que solo sé sobre el universo de Pokémon'."
    )
}

def obtener_lista_pokemon():
    """Obtiene la lista de nombres de Pokémon desde la PokeAPI o desde el archivo local."""
    if os.path.exists(ARCHIVO_POKEMON):
        try:
            with open(ARCHIVO_POKEMON, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar la lista de Pokémon desde el archivo: {e}")

    # Si el archivo no existe o hay un error, obtener la lista desde la PokeAPI
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        nombres_pokemon = [pokemon["name"] for pokemon in data["results"]]

        # Guardar la lista en el archivo local
        with open(ARCHIVO_POKEMON, "w") as f:
            json.dump(nombres_pokemon, f)

        return nombres_pokemon
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de Pokémon: {e}")
        return []

lista_pokemon = obtener_lista_pokemon()

def obtener_sprite_pokemon(nombre_pokemon):
    """Obtiene el sprite de un Pokémon desde la PokeAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre_pokemon.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        sprite_url = data["sprites"]["front_default"]
        return sprite_url
    
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el sprite: {e}")
        return None

def chatbot(prompt, historial_conversacion):
    global lista_pokemon
    if prompt.lower() == "actualizar lista pokemon":
        lista_pokemon = obtener_lista_pokemon()
        return "Lista de Pokémon actualizada.", []                          #Retorna la respuesta y una lista vacía de archivos adjuntos.

    # Crear la lista de mensajes para enviar al modelo
    mensajes = [system_message]

    # Agregar el historial solo si no está vacío
    if historial_conversacion:
        mensajes.extend(historial_conversacion)

    mensajes.append({"role": "user", "content": prompt})
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemma-3-27b-it:free",#"google/gemini-2.0-pro-exp-02-05:free",
        "messages": mensajes,
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"], []
        except KeyError:
            print("Error: La respuesta de la API no tiene la clave 'choices'.")
            print("Respuesta completa:", response.json())
            return "Ocurrió un error al procesar la respuesta.", []
        except Exception as e:
            print(f"Error inesperado: {e}")
            return "Ocurrió un error inesperado al procesar la respuesta.", []
    else:
        print(f"Error en la petición a la API. Código de estado: {response.status_code}")
        print("Respuesta de la API:", response.text)
        return f"Error {response.status_code}: {response.text}", []

def resumir_respuesta(respuesta):
    """Resumir la respuesta usando el modelo Gemini 2.0."""
    prompt_resumir = f"Resumir el siguiente texto a menos de 1900 caracteres:\n\n{respuesta}"
    mensajes_resumir = [
        {"role": "system", "content": "Eres un experto en resumir textos."},
        {"role": "user", "content": prompt_resumir}
    ]
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemma-3-27b-it:free",#"google/gemini-2.0-pro-exp-02-05:free",
        "messages": mensajes_resumir,
    }

# Bucle para probar el chatbot en consola
"""
historial_conversacion = []
while True:
    user_input = input("Tú: ")
    if user_input.lower() == "salir":
        break
    respuesta = chatbot(user_input, historial_conversacion)
    print("Profesor Oak:", respuesta)

    # Actualizar el historial de la conversación
    historial_conversacion.append({"role": "user", "content": user_input})
    historial_conversacion.append({"role": "assistant", "content": respuesta})

"""

# Bot en discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

historial_conversaciones = {}                                               #Diccionario para almacenar el historial de cada usuario.

@bot.event
async def on_ready():
    print(f'¡Un {bot.user.name} salvaje apareció!')
    
    # Modificar el estado del bot
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='/oak'))

    # Sincronizar los comandos de barra inclinada
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos.")
    except Exception as e:
        print(e)

#@bot.command()
# Registrar un comando de barra inclinada
@bot.tree.command(name="oak", description="Preguntale al Profesor Oak sobre el mundo Pokémon.")
async def oak_command(interaction: discord.Interaction, pregunta: str): #Se agrega el parametro pregunta.
    print(pregunta)                                                         #Imprime la pregunta en consola.
    
    # HISTORIAL DEL USUARIO CON EL BOT
    usuario_id = interaction.user.id                                        #Se obtiene el id del usuario.
    if usuario_id not in historial_conversaciones:                          #Se verifica si el usuario tiene historial.
        historial_conversaciones[usuario_id] = []                           #Se crea el historial del usuario.
    historial_usuario = historial_conversaciones[usuario_id]                #Se obtiene el historial del usuario.
        
    await interaction.response.defer()                                      #Muestra "está escribiendo..."
    respuesta, archivos_adjuntos = chatbot(pregunta, historial_usuario)
    
    # Identificar todos los Pokémon mencionados en la respuesta
    nombres_pokemon_respuesta = re.findall(r"\b(" + "|".join(lista_pokemon) + r")\b", respuesta, re.IGNORECASE)

    pokemon_vistos = set()                                                      #Conjunto para almacenar los pokemon vistos.
    print(f"Pokémon vistos iniciales: {pokemon_vistos}")
    sprites_mostrados = 0                                                           #Contador de sprites mostrados.

    for nombre_pokemon in nombres_pokemon_respuesta:
        print(f"Procesando Pokémon: {nombre_pokemon}")
        if nombre_pokemon not in pokemon_vistos and sprites_mostrados < 10:         #Verificar si el pokemon no esta en los vistos.
            sprite_url = obtener_sprite_pokemon(nombre_pokemon)
            print(f"Sprite del API: {sprite_url}")
            if sprite_url:
                try:
                    response_imagen = requests.get(sprite_url)
                    response_imagen.raise_for_status()
                    archivo_imagen = BytesIO(response_imagen.content)
                    archivo_discord = discord.File(archivo_imagen, filename=f"{nombre_pokemon}.png")
                    archivos_adjuntos.append(archivo_discord)
                    pokemon_vistos.add(nombre_pokemon)                              #Se agrega el pokemon a los vistos.
                    print(f"Pokémon vistos actualizados: {pokemon_vistos}")
                    sprites_mostrados += 1
                except requests.exceptions.RequestException as e:
                    print(f"Error al descargar la imagen de {nombre_pokemon}: {e}")

    if len(respuesta) >= 1900:
        respuesta = resumir_respuesta(respuesta)                                    #Resumir la respuesta.
    
    await interaction.followup.send(respuesta, files=archivos_adjuntos)             #Envia el mensaje y los archivos adjuntos

    # Actualizar el historial de la conversación
    historial_usuario.append({"role": "user", "content": pregunta})
    historial_usuario.append({"role": "assistant", "content": respuesta})

bot.run(discord_token)
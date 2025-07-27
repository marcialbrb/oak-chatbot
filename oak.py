# Estructura principal optimizada del bot "Profesor Oak" para Discord
# Usa Gemini 2.5 via OpenRouter + PokéAPI con interpretación inteligente de nombres alternativos

import os
import re
import json
import requests
from io import BytesIO

import discord
from discord.ext import commands
from aiohttp import web
import asyncio

# === CONFIGURACIONES ===
API_KEY = os.environ['API_KEY']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
ARCHIVO_POKEMON = "pokemon_list.json"

# === MENSAJE SISTEMA ===
system_message = {
    "role": "system",
    "content": (
        "Eres el Profesor Oak, un experto en el universo Pokémon. Puedes responder preguntas generales y especificas sobre Pokémon."
        "Tus respuestas serán concisas y con tono de profesor Pokémon, pero con el característico humor del Profesor Oak. Si te preguntan algo fuera de Pokémon, responde que no tienes información sobre eso."
    )
}

# === UTILS ===
def obtener_lista_pokemon():
    if os.path.exists(ARCHIVO_POKEMON):
        try:
            with open(ARCHIVO_POKEMON, "r") as f:
                return json.load(f)
        except:
            pass

    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        nombres_pokemon = [pokemon["name"] for pokemon in data["results"]]
        with open(ARCHIVO_POKEMON, "w") as f:
            json.dump(nombres_pokemon, f)
        return nombres_pokemon
    except:
        return []

lista_pokemon = obtener_lista_pokemon()


def obtener_sprite_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["sprites"]["front_default"]
    except:
        return None


def consulta_openrouter(modelo, mensajes):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"model": modelo, "messages": mensajes}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    return f"Error {response.status_code}: {response.text}"


def resumir_respuesta(respuesta):
    prompt_resumir = f"Resume este texto a menos de 1900 caracteres, conservando la información esencial:\n\n{respuesta}"
    mensajes = [
        {"role": "system", "content": "Eres un experto en resumir texto largo de forma clara y concisa."},
        {"role": "user", "content": prompt_resumir}
    ]
    return consulta_openrouter("google/gemini-2.5-flash-lite", mensajes)


cache_formas = {}
def mapear_nombre_a_forma_api(descripcion):
    if descripcion in cache_formas:
        return cache_formas[descripcion]

    prompt = (
        "Convierte esta descripción de un Pokémon o su forma a un nombre válido para consultar en la PokéAPI (/pokemon/).\n"
        "Ejemplos:\n"
        "Mega Charizard X -> charizard-mega-x\n"
        "Meowth de Alola -> meowth-alola\n"
        "Rotom lavadora -> rotom-wash\n"
        "Deoxys forma ataque -> deoxys-attack\n"
        "Zacian forma corona -> zacian-crowned\n"
        f"Descripción: {descripcion}\nResultado solo con el nombre correcto:"
    )

    mensajes = [{"role": "user", "content": prompt}]
    resultado = consulta_openrouter("google/gemini-2.5-flash-lite", mensajes).lower()
    cache_formas[descripcion] = resultado
    return resultado


def chatbot(prompt, historial):
    if prompt.lower() == "actualizar lista pokemon":
        global lista_pokemon
        lista_pokemon = obtener_lista_pokemon()
        return "Lista actualizada.", []

    mensajes = [system_message] + historial + [{"role": "user", "content": prompt}]
    respuesta = consulta_openrouter("google/gemini-2.5-flash-lite", mensajes)
    return respuesta, []


# === DISCORD BOT ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
historial_conversaciones = {}

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user.name}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='/oak'))
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(e)


@bot.tree.command(name="oak", description="Preguntale al Profesor Oak sobre el mundo Pokémon.")
async def oak_command(interaction: discord.Interaction, pregunta: str):
    user_id = interaction.user.id
    historial = historial_conversaciones.get(user_id, [])

    await interaction.response.defer()
    respuesta, archivos_adjuntos = chatbot(pregunta, historial)

    if len(respuesta) > 1900:
        respuesta = resumir_respuesta(respuesta)

    frases = re.findall(r"\b(?:\w+[\s-]+\w+|\w+)\b", respuesta.lower())
    pokemons_detectados = []
    for frase in frases:
        nombre = mapear_nombre_a_forma_api(frase)
        if nombre in lista_pokemon or "-" in nombre:
            pokemons_detectados.append(nombre)

    sprites_enviados = 0
    archivos_adjuntos = []
    for nombre in set(pokemons_detectados):
        if sprites_enviados >= 10:
            break
        url = obtener_sprite_pokemon(nombre)
        if url:
            try:
                img = requests.get(url)
                img.raise_for_status()
                archivo = BytesIO(img.content)
                archivos_adjuntos.append(discord.File(archivo, filename=f"{nombre}.png"))
                sprites_enviados += 1
            except:
                continue

    historial += [
        {"role": "user", "content": pregunta},
        {"role": "assistant", "content": respuesta}
    ]
    historial_conversaciones[user_id] = historial

    await interaction.followup.send(respuesta, files=archivos_adjuntos)


@bot.tree.command(name="sprite", description="Obtén el sprite de un Pokémon o forma especial.")
async def sprite_command(interaction: discord.Interaction, descripcion: str):
    await interaction.response.defer()
    nombre_api = mapear_nombre_a_forma_api(descripcion)
    sprite_url = obtener_sprite_pokemon(nombre_api)
    if sprite_url:
        try:
            img = requests.get(sprite_url)
            img.raise_for_status()
            archivo = BytesIO(img.content)
            await interaction.followup.send(f"Sprite de **{descripcion}** ({nombre_api}):", file=discord.File(archivo, filename=f"{nombre_api}.png"))
        except:
            await interaction.followup.send("No se pudo descargar el sprite.")
    else:
        await interaction.followup.send("No encontré información de ese Pokémon o forma.")


# === WEB SERVER PARA RENDER ===
async def handle(request):
    return web.Response(text="Profesor Oak online!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

async def main():
    await start_web_server()
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())

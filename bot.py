import re
import requests
from io import BytesIO

import discord
from discord.ext import commands

from config import MAX_SPRITES, MAX_CHARS_DISCORD
from ai_client import obtener_respuesta, resumir_respuesta
from pokeapi import cargar_lista_pokemon, actualizar_lista_pokemon, obtener_sprite_pokemon


# === Setup del bot ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Estado en memoria
lista_pokemon: list[str] = []
historial_conversaciones: dict[int, list[dict]] = {}


# === Helpers ===

def _descargar_sprite(nombre: str) -> discord.File | None:
    """Descarga el sprite de un Pokémon y lo devuelve como archivo de Discord."""
    sprite_url = obtener_sprite_pokemon(nombre)
    if not sprite_url:
        return None
    try:
        response = requests.get(sprite_url)
        response.raise_for_status()
        archivo = BytesIO(response.content)
        return discord.File(archivo, filename=f"{nombre}.png")
    except requests.RequestException as e:
        print(f"Error al descargar sprite de {nombre}: {e}")
        return None


def _extraer_sprites(respuesta: str) -> list[discord.File]:
    """Extrae hasta MAX_SPRITES sprites de los Pokémon mencionados en la respuesta."""
    patron = r"\b(" + "|".join(lista_pokemon) + r")\b"
    mencionados = re.findall(patron, respuesta, re.IGNORECASE)

    archivos = []
    vistos = set()

    for nombre in mencionados:
        if nombre in vistos or len(archivos) >= MAX_SPRITES:
            continue
        sprite = _descargar_sprite(nombre)
        if sprite:
            archivos.append(sprite)
            vistos.add(nombre)

    return archivos


# === Eventos ===

@bot.event
async def on_ready():
    global lista_pokemon
    lista_pokemon = cargar_lista_pokemon()

    print(f"¡Un {bot.user.name} salvaje apareció!")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="/oak")
    )

    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# === Comandos ===

@bot.tree.command(name="oak", description="Preguntale al Profesor Oak sobre el mundo Pokémon.")
async def oak_command(interaction: discord.Interaction, pregunta: str):
    print(f"[{interaction.user}] {pregunta}")
    await interaction.response.defer()

    # Historial por usuario
    usuario_id = interaction.user.id
    historial = historial_conversaciones.setdefault(usuario_id, [])

    # Caso especial: actualizar lista
    if pregunta.strip().lower() == "actualizar lista pokemon":
        global lista_pokemon
        lista_pokemon = actualizar_lista_pokemon()
        await interaction.followup.send("✅ Lista de Pokémon actualizada.")
        return

    # Generar respuesta
    respuesta = obtener_respuesta(pregunta, historial)

    # Resumir si excede el límite de Discord
    if len(respuesta) >= MAX_CHARS_DISCORD:
        respuesta = resumir_respuesta(respuesta)

    # Obtener sprites de los Pokémon mencionados
    sprites = _extraer_sprites(respuesta)

    await interaction.followup.send(respuesta, files=sprites)

    respuesta = obtener_respuesta(pregunta, historial)

    if respuesta.startswith("Error"):
        await interaction.followup.send(respuesta)
        return  # No actualizar historial si hubo error

    if len(respuesta) >= MAX_CHARS_DISCORD:
        respuesta = resumir_respuesta(respuesta)

    sprites = _extraer_sprites(respuesta)
    await interaction.followup.send(respuesta, files=sprites)

    # Solo guardar en historial si todo salió bien
    historial.append({"role": "user", "content": pregunta})
    historial.append({"role": "assistant", "content": respuesta})
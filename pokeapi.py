import json
import os
import requests
from config import ARCHIVO_POKEMON


def cargar_lista_pokemon() -> list[str]:
    """Carga la lista de Pokémon desde archivo local o desde la PokeAPI si no existe."""
    if os.path.exists(ARCHIVO_POKEMON):
        try:
            with open(ARCHIVO_POKEMON, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar lista local de Pokémon: {e}")

    return _obtener_lista_desde_api()


def _obtener_lista_desde_api() -> list[str]:
    """Descarga la lista de Pokémon desde la PokeAPI y la guarda localmente."""
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        nombres = [p["name"] for p in response.json()["results"]]

        with open(ARCHIVO_POKEMON, "w") as f:
            json.dump(nombres, f)

        print(f"Lista de Pokémon actualizada: {len(nombres)} entradas.")
        return nombres

    except requests.RequestException as e:
        print(f"Error al obtener lista de Pokémon desde la API: {e}")
        return []


def actualizar_lista_pokemon() -> list[str]:
    """Fuerza la actualización de la lista desde la PokeAPI."""
    return _obtener_lista_desde_api()


def obtener_sprite_pokemon(nombre: str) -> str | None:
    """Devuelve la URL del sprite frontal de un Pokémon, o None si no se encuentra."""
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["sprites"]["front_default"]
    except requests.RequestException as e:
        print(f"Error al obtener sprite de {nombre}: {e}")
        return None

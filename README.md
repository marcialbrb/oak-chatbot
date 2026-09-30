![Profesor-Oak](https://github.com/user-attachments/assets/13254bdd-9269-4410-8525-8bc4de5d1dab)

# 🎓 Profesor Oak — Bot de Discord

Un bot de Discord que encarna al **Profesor Oak**, la mayor eminencia del mundo Pokémon. Preguntale lo que quieras sobre estadísticas, evoluciones, rutas, tipos, habilidades, movimientos o armado de equipos, y te responde con su personalidad sabia, amable y levemente filosófica. Además, acompaña la respuesta con los **sprites** de los Pokémon mencionados.

[**➕ Invitar al bot a tu servidor**](https://discord.com/oauth2/authorize?client_id=1345610366897360906) _(necesitás permisos de administrador en el servidor)_

---

## 📖 Por qué existe

Es el primer chatbot que creé. Siempre fui de googlear a qué nivel evolucionaba tal Pokémon, qué stat base era el más alto o en qué ruta aparecía, todo mientras jugaba en la 3DS o en la GBA. Oak fue uno de los primeros personajes del universo Pokémon, así que me pareció emblemático personificarlo y dejar todas esas consultas al alcance de un chat de Discord.

## ✨ Características

- **Comando `/oak`**: hacé tu pregunta con un slash command y Oak responde en el mismo canal.
- **Personalidad fiel al personaje**: responde en el idioma en que le hablen, con tono sabio y conciso.
- **Sprites automáticos**: detecta los Pokémon mencionados en la respuesta y adjunta su sprite (hasta 10 por mensaje), obtenido de la [PokeAPI](https://pokeapi.co/).
- **Tolerante a errores de tipeo**: si escribís mal un nombre, intenta deducir a qué Pokémon te referís.
- **Formas regionales y especiales**: entiende nombres como `pikachu-alola` o `charizard-mega-x`.
- **Nombres oficiales**: movimientos, habilidades y naturalezas en español de España, con el nombre en inglés entre paréntesis (ej: *Rayo Hielo (Ice Beam)*).
- **Memoria de conversación**: recuerda los últimos mensajes de cada usuario para mantener el contexto.
- **Respuestas que caben en Discord**: si una respuesta supera el límite de caracteres, Oak la resume automáticamente.
- **Se mantiene en su área**: si la pregunta no tiene que ver con Pokémon, redirige amablemente la charla.

## 💬 Uso

```
/oak pregunta: ¿A qué nivel evoluciona Charmander?
/oak pregunta: Armame un equipo competitivo con Garchomp
/oak pregunta: ¿En qué ruta aparece Eevee en Pokémon Amarillo?
```

### Comandos especiales

Se escriben como si fueran una pregunta normal en `/oak`:

| Pregunta | Qué hace |
| --- | --- |
| `limpiar historial` | Borra el historial de conversación del usuario. |
| `actualizar lista pokemon` | Vuelve a descargar la lista de Pokémon desde la PokeAPI. |

## 🛠️ Stack

- **Python 3** con [discord.py](https://github.com/Rapptz/discord.py)
- **[OpenRouter](https://openrouter.ai/)** como gateway de IA, usando el modelo `deepseek/deepseek-chat-v3-0324`
- **[PokeAPI](https://pokeapi.co/)** para la lista de Pokémon y los sprites
- **aiohttp** para el servidor HTTP de health check
- Deploy en **[Render](https://render.com/)**

## 🗂️ Estructura del proyecto

```
├── main.py             # Punto de entrada: levanta el servidor web y el bot
├── bot.py              # Bot de Discord, comando /oak, manejo de historial y sprites
├── ai_client.py        # Cliente de OpenRouter (respuestas y resúmenes)
├── pokeapi.py          # Lista de Pokémon y sprites desde la PokeAPI
├── config.py           # Configuración, límites y prompt del sistema de Oak
├── server.py           # Servidor HTTP en el puerto 8080 (requerido por Render)
├── pokemon_list.json   # Caché local de nombres de Pokémon
└── procfile            # Comando de arranque para el deploy
```

## 🚀 Correrlo en tu máquina

### 1. Requisitos

- Python 3.10 o superior
- Un bot creado en el [Discord Developer Portal](https://discord.com/developers/applications) con el **Message Content Intent** activado
- Una API key de [OpenRouter](https://openrouter.ai/keys)

### 2. Instalación

```bash
git clone <url-del-repositorio>
cd <carpeta-del-repositorio>

python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

pip install discord.py aiohttp requests
```

### 3. Variables de entorno

| Variable | Descripción |
| --- | --- |
| `API_KEY` | API key de OpenRouter |
| `DISCORD_TOKEN` | Token del bot de Discord |

```bash
export API_KEY="tu-api-key-de-openrouter"
export DISCORD_TOKEN="tu-token-de-discord"
```

### 4. Ejecutar

```bash
python main.py
```

Al iniciar, el bot carga la lista de Pokémon (desde `pokemon_list.json`, o desde la PokeAPI si el archivo no existe) y sincroniza los slash commands.

## ☁️ Deploy en Render

El proyecto está pensado para correr como **Web Service** en Render:

1. Conectá el repositorio y configurá el comando de inicio como `python main.py` (el `procfile` ya lo define).
2. Cargá las variables `API_KEY` y `DISCORD_TOKEN` en el panel de entorno.
3. `server.py` expone un endpoint `/` en el puerto `8080`, que Render usa para verificar que el servicio está vivo.

## ⚙️ Configuración

Los parámetros principales están en `config.py`:

| Parámetro | Valor | Descripción |
| --- | --- | --- |
| `MODEL` | `deepseek/deepseek-chat-v3-0324` | Modelo usado vía OpenRouter |
| `MAX_SPRITES` | `10` | Máximo de sprites por respuesta |
| `MAX_CHARS_DISCORD` | `1900` | Largo a partir del cual la respuesta se resume |
| `MAX_HISTORIAL` | `6` | Mensajes recordados por usuario |
| `SYSTEM_MESSAGE` | — | Prompt que define la personalidad y las reglas de Oak |

## 🤝 Contribuir

Ideas, bugs y mejoras son bienvenidos: abrí un issue o mandá un pull request.

## 💌 Contacto

Fue divertido hacerlo. Si lo usás, avisame 🙂

---

_Pokémon y sus personajes son marca registrada de Nintendo, Game Freak y The Pokémon Company. Este es un proyecto de fans sin fines de lucro y no está afiliado a ninguna de ellas._

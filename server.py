from aiohttp import web


async def _handle(request):
    return web.Response(text="Oak está en línea y listo para responder preguntas sobre Pokémon!")


async def iniciar_servidor():
    """Levanta un servidor HTTP en el puerto 8080 (requerido por Render)."""
    app = web.Application()
    app.add_routes([web.get("/", _handle)])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Servidor web iniciado en el puerto 8080.")

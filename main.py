from aiohttp import web
import asyncio
from raid import application
import os

async def handle(request):
    return web.Response(text="🤖 Bot is running!")

async def start_bot():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

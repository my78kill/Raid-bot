# main.py
import asyncio
from raid import application

async def main():
    # Initialize + start bot
    await application.initialize()
    await application.start()
    # Polling + idle
    await application.updater.start_polling()
    await application.updater.idle()

# Run the async main loop
asyncio.run(main())

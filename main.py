from flask import Flask
import asyncio
from raid import application
import os
import threading

app = Flask(__name__)

# Simple health endpoint
@app.route("/")
def home():
    return "🤖 Bot is running!"

# Async bot runner
async def start_bot():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    # Run bot in a separate thread
    threading.Thread(target=run_bot).start()

    # Run Flask server on Render port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask
import threading
from raid import application
import asyncio
import os

app = Flask(__name__)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling(drop_pending_updates=True)

@app.route("/")
def home():
    return "🤖 Bot is running!"

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

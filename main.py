from flask import Flask
import threading
from raid import application  # your bot

app = Flask(__name__)

def run_bot():
    application.run_polling(drop_pending_updates=True)

@app.route("/")
def home():
    return "🤖 Bot is running!"

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

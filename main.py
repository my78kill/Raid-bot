# main.py
from raid import application
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is running!"

if __name__ == "__main__":
    # Run the bot in main thread
    application.run_polling(drop_pending_updates=True)

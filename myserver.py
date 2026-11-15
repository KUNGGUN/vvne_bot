import os
from threading import Thread

from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/")
def home():
    return "VVNE BOT Server is running!", 200

@app.route("/health")
def health():
    return "OK", 200

def run():
    port = int(os.environ.get("PORT", 10000))

    serve(
        app,
        host="0.0.0.0",
        port=port
    )

def server_on():
    thread = Thread(
        target=run,
        daemon=True
    )
    thread.start()

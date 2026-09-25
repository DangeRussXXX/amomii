from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_command = ""

@app.post("/command")
def command():
    global latest_command
    latest_command = request.data.decode().strip()
    return "OK"

@app.get("/command")
def get_command():
    return latest_command

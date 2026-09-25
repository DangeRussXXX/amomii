from flask import Flask, request

app = Flask(__name__)

latest_command = ""

@app.post("/command")
def command():
    global latest_command
    latest_command = request.data.decode().strip()
    return "OK"

@app.get("/command")
def get_command():
    return latest_command
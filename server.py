from flask import Flask, request
import serial

# Create Flask app
app = Flask(__name__)

# Arduino serial setup
# IMPORTANT: This will NOT work on Render because Render cannot access COM ports.
# You will need a relay client on your PC later.
ser = serial.Serial("COM9", 9600, timeout=1)

@app.post("/command")
def command():
    cmd = request.data.decode().strip()
    ser.write((cmd + "\n").encode())
    return "OK"

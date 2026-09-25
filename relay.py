import time
import serial
import requests

# Your Arduino
ser = serial.Serial("COM9", 9600, timeout=1)

# Your Render server URL
SERVER_URL = "https://amomii-server.onrender.com/command"

last_sent = ""

while True:
    try:
        cmd = requests.get(SERVER_URL).text.strip()

        if cmd and cmd != last_sent:
            print("Sending to Arduino:", cmd)
            ser.write((cmd + "\n").encode())
            last_sent = cmd

    except Exception as e:
        print("Error:", e)

    time.sleep(1)

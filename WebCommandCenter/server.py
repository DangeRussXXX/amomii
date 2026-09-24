import serial
import time

ARDUINO_PORT = "COM9"
BAUD = 9600

arduino = serial.Serial(ARDUINO_PORT, BAUD, timeout=1)

time.sleep(2)

print("Arduino connected on COM9")
print("Type commands:")
print("  led on")
print("  led off")
print("  trainer 0 on")
print("  trainer 0 off")
print("  trainer 3 on")
print("  trainer 7 on")
print("  quit")

while True:

    command = input("> ").strip()

    if command.lower() == "quit":
        break

    arduino.write((command + "\n").encode())

    time.sleep(0.1)

    while arduino.in_waiting:
        response = arduino.readline().decode(errors="ignore").strip()

        if response:
            print("[Arduino]", response)

arduino.close()
print("Disconnected.")

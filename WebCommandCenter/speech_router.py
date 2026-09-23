import serial
import time

# CHANGE THIS to your Arduino COM port
ARDUINO_PORT = "COM3"
BAUD = 9600

# Open Arduino serial port
arduino = serial.Serial(ARDUINO_PORT, BAUD, timeout=1)
time.sleep(2)

print("========================================")
print("     GOOGLE SPEECH → ARDUINO ROUTER")
print("========================================")
print("Router online. Speak commands...")
print()

# Number word map
word_map = {
    "zero": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "oh": "0"
}

def normalize_voice(text):
    text = text.lower()

    # Fix "trainer led" → "trainerled"
    if "trainer led" in text:
        text = text.replace("trainer led", "trainerled")

    # Remove spaces
    compact = text.replace(" ", "")

    # Replace number words
    for word, digit in word_map.items():
        if word in compact:
            compact = compact.replace(word, digit)

    return compact

def send_to_arduino(cmd):
    arduino.write((cmd + "\n").encode())
    time.sleep(0.1)

    # Read Arduino response
    response = arduino.readline().decode().strip()
    if response:
        print("[Arduino] " + response)

print("READY.")

while True:
    # Your voice program must pass the recognized text HERE
    voice_text = input("[Voice] ")

    if not voice_text:
        continue

    # Normalize trainer LED commands
    cmd = normalize_voice(voice_text)

    print("[Router] Sending:", cmd)

    # Send to Arduino
    send_to_arduino(cmd)

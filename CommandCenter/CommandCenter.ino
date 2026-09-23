import serial
import time
import speech_recognition as sr

# CHANGE THIS to your Arduino COM port
ARDUINO_PORT = "COM3"
BAUD = 9600

# Open Arduino serial port
arduino = serial.Serial(ARDUINO_PORT, BAUD, timeout=1)
time.sleep(2)

print("========================================")
print("     VOICE → ARDUINO COMMAND ROUTER")
print("========================================")
print("Speak commands like:")
print("  trainer LED zero on")
print("  trainer LED one off")
print("  LED on")
print("  LED off")
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

# Speech recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

print("Voice system ready.")

while True:
    with mic as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        voice_text = recognizer.recognize_google(audio)
        print("[Voice] " + voice_text)

        # Normalize trainer LED commands
        cmd = normalize_voice(voice_text)
        print("[Router] Sending:", cmd)

        # Send to Arduino
        send_to_arduino(cmd)

    except sr.UnknownValueError:
        print("[Voice] Could not understand.")
    except sr.RequestError as e:
        print("[Voice] Speech service error:", e)

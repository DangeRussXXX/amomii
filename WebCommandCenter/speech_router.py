import serial
import time

# ============================================================
# GOOGLE SPEECH → ARDUINO ROUTER
# ============================================================

ARDUINO_PORT = "COM3"
BAUD = 9600

arduino = serial.Serial(
    ARDUINO_PORT,
    BAUD,
    timeout=1
)

time.sleep(2)

print("========================================")
print("     GOOGLE SPEECH → ARDUINO ROUTER")
print("========================================")
print("Router online.")
print()
print("Try:")
print("  trainer led three on")
print("  trainer led three off")
print("  trainer led seven on")
print("  trainer led zero off")
print()


# ============================================================
# NUMBER WORDS
# ============================================================

WORD_MAP = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "oh": "0"
}


# ============================================================
# NORMALIZE VOICE
# ============================================================

def normalize_voice(text):

    text = text.lower().strip()

    # --------------------------------------------------------
    # Remove common speech-command filler
    # --------------------------------------------------------

    text = text.replace("please ", "")
    text = text.replace("turn on ", "")
    text = text.replace("turn off ", "")
    text = text.replace("turn ", "")
    text = text.replace("switch on ", "")
    text = text.replace("switch off ", "")
    text = text.replace("switch ", "")

    # --------------------------------------------------------
    # Normalize trainer LED wording
    # --------------------------------------------------------

    text = text.replace("trainer leds", "trainer led")
    text = text.replace("trainer lights", "trainer led")
    text = text.replace("trainer light", "trainer led")

    # --------------------------------------------------------
    # Convert "trainer led" → "trainerled"
    # --------------------------------------------------------

    text = text.replace("trainer led", "trainerled")

    # --------------------------------------------------------
    # Convert number words
    #
    # Do this BEFORE removing spaces so "three" remains
    # recognizable.
    # --------------------------------------------------------

    words = text.split()

    converted = []

    for word in words:

        if word in WORD_MAP:
            converted.append(WORD_MAP[word])
        else:
            converted.append(word)

    text = "".join(converted)

    return text


# ============================================================
# SEND TO ARDUINO
# ============================================================

def send_to_arduino(cmd):

    print("[Router] Sending:", cmd)

    arduino.write((cmd + "\n").encode())

    time.sleep(0.15)

    while arduino.in_waiting:

        response = arduino.readline().decode(
            errors="ignore"
        ).strip()

        if response:
            print("[Arduino]", response)


# ============================================================
# MAIN LOOP
# ============================================================

print("READY.")
print()

while True:

    try:

        voice_text = input("[Voice] ")

        if not voice_text.strip():
            continue

        cmd = normalize_voice(voice_text)

        print("[Normalized]:", cmd)

        send_to_arduino(cmd)

    except KeyboardInterrupt:

        print()
        print("Router shutting down.")

        arduino.close()

        break
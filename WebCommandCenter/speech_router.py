import serial
import time
import re

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
print("Examples:")
print("  led on")
print("  led off")
print("  trainer led three on")
print("  trainer led three off")
print("  turn on trainer led three")
print("  turn off trainer led three")
print()


# ============================================================
# NUMBER WORDS
# ============================================================

NUMBER_WORDS = {
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
# NORMALIZE VOICE COMMAND
# ============================================================

def normalize_voice(text):

    text = text.lower().strip()

    # ----------------------------------------
    # Clean punctuation
    # ----------------------------------------

    text = re.sub(r"[.,!?]", "", text)

    # ----------------------------------------
    # Convert number words FIRST
    # ----------------------------------------

    words = text.split()

    converted = []

    for word in words:

        if word in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[word])
        else:
            converted.append(word)

    words = converted

    # ----------------------------------------
    # Find ON / OFF
    # ----------------------------------------

    is_on = "on" in words
    is_off = "off" in words

    # ----------------------------------------
    # Built-in LED
    # ----------------------------------------

    if "led" in words and not ("trainer" in words):

        if is_on:
            return "ledon"

        if is_off:
            return "ledoff"

    # ----------------------------------------
    # Trainer LED
    # ----------------------------------------

    if "trainer" in words:

        # Find "led" after trainer
        if "led" in words:

            led_position = words.index("led")

            # Number should normally follow LED
            if led_position + 1 < len(words):

                number = words[led_position + 1]

                if number.isdigit():

                    index = int(number)

                    if 0 <= index <= 7:

                        if is_off:
                            return f"trainerled{index}off"

                        if is_on:
                            return f"trainerled{index}on"

    # ----------------------------------------
    # Other existing commands
    # ----------------------------------------

    # Remove spaces for simple Arduino commands
    compact = "".join(words)

    return compact


# ============================================================
# SEND COMMAND
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
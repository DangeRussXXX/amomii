import serial
import time
import re

# ============================================================
# AMOMII ONE - NATURAL COMMAND ROUTER
# ============================================================

ARDUINO_PORT = "COM9"
BAUD = 9600

arduino = serial.Serial(
    ARDUINO_PORT,
    BAUD,
    timeout=1
)

time.sleep(2)

print("========================================")
print("      AMOMII NATURAL COMMAND ROUTER")
print("========================================")
print("Arduino: COM9")
print()
print("Try:")
print("  led on")
print("  led off")
print("  trainer led three on")
print("  trainer led three off")
print("  turn on trainer led seven")
print("  turn off trainer led seven")
print()
print("Type quit to exit.")
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
}


# ============================================================
# NORMALIZE COMMAND
# ============================================================

def normalize_command(text):

    text = text.lower().strip()

    # Remove punctuation
    text = re.sub(r"[.,!?]", "", text)

    words = text.split()

    # --------------------------------------------------------
    # Convert number words
    # --------------------------------------------------------

    words = [
        NUMBER_WORDS.get(word, word)
        for word in words
    ]

    # --------------------------------------------------------
    # Built-in LED
    # --------------------------------------------------------

    if "led" in words and "trainer" not in words:

        if "on" in words:
            return "led on"

        if "off" in words:
            return "led off"

    # --------------------------------------------------------
    # Trainer LED
    # --------------------------------------------------------

    if "trainer" in words and "led" in words:

        try:

            led_position = words.index("led")

            number = words[led_position + 1]

            index = int(number)

            if 0 <= index <= 7:

                if "on" in words:
                    return f"trainer {index} on"

                if "off" in words:
                    return f"trainer {index} off"

        except (ValueError, IndexError):
            pass

    # --------------------------------------------------------
    # Already-clean trainer command
    # --------------------------------------------------------

    if len(words) == 3:

        if words[0] == "trainer":

            try:

                index = int(words[1])

                if 0 <= index <= 7:

                    if words[2] in ("on", "off"):
                        return f"trainer {index} {words[2]}"

            except ValueError:
                pass

    # --------------------------------------------------------
    # Unknown command
    # --------------------------------------------------------

    return None


# ============================================================
# SEND COMMAND
# ============================================================

def send_command(command):

    print("[Arduino TX]", command)

    arduino.write(
        (command + "\n").encode()
    )

    arduino.flush()

    time.sleep(0.1)

    while arduino.in_waiting:

        response = arduino.readline().decode(
            errors="ignore"
        ).strip()

        if response:
            print("[Arduino]", response)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    try:

        voice_text = input("> ")

    except KeyboardInterrupt:

        break

    if voice_text.lower().strip() == "quit":
        break

    if not voice_text.strip():
        continue

    command = normalize_command(voice_text)

    print("[Router]", command)

    if command is None:

        print("[Router] I don't understand that command.")
        continue

    send_command(command)


arduino.close()

print()
print("AMOMII router stopped.")
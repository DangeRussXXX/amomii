from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import serial
import time
import re

# ============================================================
# AMOMII ONE
# WEB VOICE COMMAND SERVER
# ============================================================

HOST = "127.0.0.1"
PORT = 8000

ARDUINO_PORT = "COM9"
BAUD = 9600


# ============================================================
# OPEN ARDUINO ONCE
# ============================================================

try:

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD,
        timeout=1
    )

    # Give Arduino time to finish resetting
    time.sleep(2)

    print("[Arduino] Connected:", ARDUINO_PORT)

except Exception as e:

    arduino = None

    print("[ERROR] Could not open Arduino:")
    print(e)


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

    # Remove punctuation
    text = re.sub(r"[.,!?]", "", text)

    words = text.split()

    # --------------------------------------------------------
    # Convert spoken numbers
    # --------------------------------------------------------

    converted = []

    for word in words:

        if word in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[word])
        else:
            converted.append(word)

    words = converted

    # --------------------------------------------------------
    # BUILT-IN LED
    # --------------------------------------------------------

    if "led" in words and "trainer" not in words:

        if "on" in words:
            return "ledon"

        if "off" in words:
            return "ledoff"

    # --------------------------------------------------------
    # TRAINER LED
    # --------------------------------------------------------

    if "trainer" in words and "led" in words:

        led_position = words.index("led")

        if led_position + 1 < len(words):

            number = words[led_position + 1]

            if number.isdigit():

                index = int(number)

                if 0 <= index <= 7:

                    if "off" in words:
                        return f"trainerled{index}off"

                    if "on" in words:
                        return f"trainerled{index}on"

    # --------------------------------------------------------
    # OTHER COMMANDS
    # --------------------------------------------------------

    # Commands such as:
    #
    # blink 10
    # speed 100
    # pulse 500
    # status
    # help
    #
    return "".join(words)


# ============================================================
# SEND TO ARDUINO
# ============================================================

def send_to_arduino(command):

    global arduino

    if arduino is None:

        print("[ERROR] Arduino is not connected.")

        return

    try:

        print("[Arduino TX]:", command)

        arduino.write(
            (command + "\n").encode()
        )

        arduino.flush()

        # Read any response
        time.sleep(0.1)

        while arduino.in_waiting:

            response = arduino.readline().decode(
                errors="ignore"
            ).strip()

            if response:
                print("[Arduino RX]:", response)

    except Exception as e:

        print("[ERROR] Serial communication failed:")
        print(e)


# ============================================================
# HTTP HANDLER
# ============================================================

class AMOMIIHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):

        print(
            f"[HTTP] {self.address_string()} - "
            f"{format % args}"
        )

    # --------------------------------------------------------
    # VOICE COMMAND
    # --------------------------------------------------------

    def do_POST(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body = self.rfile.read(
                length
            ).decode(
                errors="ignore"
            ).strip()

            print()
            print("[VOICE] Received:", body)

            if not body:

                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    b"Empty command"
                )

                return

            # Normalize
            cmd = normalize_voice(body)

            print("[Router] Normalized:", cmd)

            # Send
            send_to_arduino(cmd)

            # HTTP response
            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain"
            )

            self.end_headers()

            self.wfile.write(
                b"OK"
            )

        except Exception as e:

            print(
                "[ERROR] HTTP command failed:",
                e
            )

            self.send_response(500)
            self.end_headers()

            self.wfile.write(
                b"ERROR"
            )


# ============================================================
# SERVER
# ============================================================

server = ThreadingHTTPServer(
    (HOST, PORT),
    AMOMIIHandler
)


print()
print("========================================")
print("       AMOMII WEB COMMAND CENTER")
print("========================================")
print()
print(f"Server: http://{HOST}:{PORT}")
print(f"Arduino: {ARDUINO_PORT}")
print(f"Baud: {BAUD}")
print()
print("Voice router ONLINE.")
print()
print("Examples:")
print("  led on")
print("  led off")
print("  trainer led three on")
print("  trainer led three off")
print("  turn on trainer led three")
print("  turn off trainer led three")
print()
print("Press CTRL+C to stop.")
print()


# ============================================================
# RUN
# ============================================================

try:

    server.serve_forever()

except KeyboardInterrupt:

    print()
    print("Stopping AMOMII server...")

finally:

    server.server_close()

    if arduino is not None:

        arduino.close()

        print("[Arduino] Serial connection closed.")

    print("Server stopped.")
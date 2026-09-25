import serial
import time
import re

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "127.0.0.1"
PORT = 8000

ARDUINO_PORT = "COM9"
BAUD = 9600


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
# ARDUINO CONNECTION
# ============================================================

arduino = None


def connect_arduino():
    global arduino

    try:
        if arduino is not None:
            try:
                arduino.close()
            except Exception:
                pass

        print(f"[Arduino] Connecting to {ARDUINO_PORT}...")

        arduino = serial.Serial(
            ARDUINO_PORT,
            BAUD,
            timeout=1
        )

        time.sleep(2)

        print("[Arduino] CONNECTED")
        return True

    except Exception as e:
        arduino = None
        print("[Arduino] CONNECTION FAILED:", e)
        return False


# ============================================================
# NORMALIZE COMMAND
# ============================================================

def normalize_command(text):

    if not text:
        return None

    text = text.lower().strip()

    text = re.sub(r"[.,!?]", "", text)

    text = re.sub(
        r"\b(the|please|a|an)\b",
        " ",
        text
    )

    text = re.sub(r"\s+", " ", text).strip()

    words = []

    for word in text.split():
        words.append(NUMBER_WORDS.get(word, word))

    # --------------------------------------------------------
    # Trainer LED
    #
    # trainer led 1 on
    # trainer 1 on
    # trainer led one on
    # turn on trainer led one
    # turn off trainer led seven
    # --------------------------------------------------------

    if "trainer" in words:

        trainer_pos = words.index("trainer")

        led_pos = None

        if "led" in words:
            led_pos = words.index("led")

        if led_pos is not None and led_pos > trainer_pos:
            number_pos = led_pos + 1
        else:
            number_pos = trainer_pos + 1

        if number_pos < len(words):

            number = words[number_pos]

            try:
                index = int(number)
            except ValueError:
                index = -1

            if 0 <= index <= 7:

                if "on" in words:
                    return f"trainerled{index}on"

                if "off" in words:
                    return f"trainerled{index}off"

        # Trainer all
        if "all" in words:

            if "on" in words:
                return "trainerallon"

            if "off" in words:
                return "traineralloff"

    # --------------------------------------------------------
    # Built-in Arduino LED
    # --------------------------------------------------------

    if "trainer" not in words:

        if "led" in words:

            if "on" in words:
                return "ledon"

            if "off" in words:
                return "ledoff"

        if "arduino" in words:

            if "on" in words:
                return "ledon"

            if "off" in words:
                return "ledoff"

    # --------------------------------------------------------
    # ALL / BOTH
    # --------------------------------------------------------

    if "all" in words:

        if "on" in words:
            return "allon"

        if "off" in words:
            return "alloff"

    if "both" in words:

        if "on" in words:
            return "allon"

        if "off" in words:
            return "alloff"

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    if "stop" in words or "halt" in words:
        return "stop"

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if "status" in words:
        return "status"

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if "help" in words or "commands" in words:
        return "help"

    return None


# ============================================================
# SEND TO ARDUINO
# ============================================================

def send_to_arduino(command):

    global arduino

    if arduino is None:

        if not connect_arduino():
            return False, "Arduino not connected"

    try:

        print("[Arduino TX]:", command)

        arduino.write(
            (command + "\n").encode("utf-8")
        )

        arduino.flush()

        time.sleep(0.15)

        while arduino.in_waiting > 0:

            response = arduino.readline().decode(
                errors="ignore"
            ).strip()

            if response:
                print("[Arduino RX]:", response)

        return True, command

    except Exception as e:

        print("[Arduino] SERIAL ERROR:", e)

        try:
            arduino.close()
        except Exception:
            pass

        arduino = None

        return False, "Arduino serial error"


# ============================================================
# PROCESS COMMAND
# ============================================================

def process_command(raw_text, source="HTTP"):

    print()
    print("========================================")
    print(f"[{source}] {raw_text}")
    print("========================================")

    command = normalize_command(raw_text)

    print("[Router] Normalized:", command)

    if command is None:
        return False, "Command not recognized"

    return send_to_arduino(command)


# ============================================================
# HTTP SERVER
# ============================================================

class AMOMIIHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print("[HTTP]", format % args)

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    def do_POST(self):

        if self.path != "/command":

            self.send_response(404)

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            return

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body = self.rfile.read(length).decode(
                "utf-8",
                errors="ignore"
            ).strip()

            print("[HTTP] Received:", body)

            if not body:

                self.send_response(400)

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )

                self.end_headers()

                self.wfile.write(
                    b"Empty command"
                )

                return

            success, result = process_command(
                body,
                "VOICE/HTTP"
            )

            if success:

                self.send_response(200)

            else:

                self.send_response(500)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.send_header(
                "Access-Control-Allow-Methods",
                "POST, OPTIONS"
            )

            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type"
            )

            self.end_headers()

            if success:
                self.wfile.write(
                    ("OK: " + result).encode("utf-8")
                )
            else:
                self.wfile.write(
                    result.encode("utf-8")
                )

        except Exception as e:

            print("[HTTP ERROR]:", e)

            try:

                self.send_response(500)

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )

                self.end_headers()

                self.wfile.write(
                    b"Server error"
                )

            except Exception:
                pass


# ============================================================
# START SERVER
# ============================================================

def start_server():

    server = ThreadingHTTPServer(
        (HOST, PORT),
        AMOMIIHandler
    )

    print()
    print("========================================")
    print("     AMOMII ONE COMMAND CENTER")
    print("========================================")
    print()
    print(f"HTTP SERVER: http://{HOST}:{PORT}")
    print(f"ARDUINO: {ARDUINO_PORT}")
    print(f"BAUD: {BAUD}")
    print()
    print("VOICE ROUTER: ONLINE")
    print("HTTP SERVER: ONLINE")
    print()
    print("========================================")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping server...")

    finally:

        server.server_close()

        if arduino is not None:

            try:
                arduino.close()
            except Exception:
                pass

        print("AMOMII Command Center stopped.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    connect_arduino()

    start_server()

import serial
import time
import re

from http.server import ThreadingHTTPServer
from http.server import SimpleHTTPRequestHandler


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
# ARDUINO
# ============================================================

arduino = None


def connect_arduino():

    global arduino

    try:

        if arduino is not None:

            try:
                arduino.close()
            except:
                pass

            arduino = None

        print()
        print("[Arduino] Connecting to", ARDUINO_PORT)

        arduino = serial.Serial(
            ARDUINO_PORT,
            BAUD,
            timeout=1
        )

        time.sleep(2)

        print("[Arduino] CONNECTED")
        print("[Arduino] Port:", ARDUINO_PORT)
        print("[Arduino] Baud:", BAUD)
        print()

        return True

    except Exception as e:

        arduino = None

        print()
        print("[Arduino] CONNECTION FAILED")
        print("[Arduino]", e)
        print()

        return False


# ============================================================
# SEND TO ARDUINO
# ============================================================

def send_to_arduino(command):

    global arduino

    if arduino is None:

        print("[Arduino] Not connected.")
        print("[Arduino] Attempting reconnect...")

        if not connect_arduino():
            return False

    try:

        print("[Arduino TX]:", command)

        arduino.write(
            (command + "\n").encode("utf-8")
        )

        arduino.flush()

        time.sleep(0.10)

        while arduino.in_waiting > 0:

            response = arduino.readline().decode(
                errors="ignore"
            ).strip()

            if response:
                print("[Arduino RX]:", response)

        print("[Arduino] Command sent successfully.")

        return True

    except Exception as e:

        print()
        print("[Arduino] SERIAL ERROR")
        print("[Arduino]", e)
        print()

        try:
            arduino.close()
        except:
            pass

        arduino = None

        return False


# ============================================================
# NORMALIZE COMMAND
# ============================================================

def normalize_command(text):

    if text is None:
        return None

    text = text.lower().strip()

    text = re.sub(
        r"[.,!?]",
        "",
        text
    )

    text = re.sub(
        r"\b(the|please|a|an)\b",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    words = text.split()

    converted = []

    for word in words:

        if word in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[word])
        else:
            converted.append(word)

    words = converted

    # ========================================================
    # TURN ON TRAINER LED
    # ========================================================

    if (
        "turn" in words
        and "on" in words
        and "trainer" in words
        and "led" in words
    ):

        try:

            led_position = words.index("led")
            number = words[led_position + 1]
            index = int(number)

            if 0 <= index <= 7:
                return f"trainer led {index} on"

        except (ValueError, IndexError):
            pass

    # ========================================================
    # TURN OFF TRAINER LED
    # ========================================================

    if (
        "turn" in words
        and "off" in words
        and "trainer" in words
        and "led" in words
    ):

        try:

            led_position = words.index("led")
            number = words[led_position + 1]
            index = int(number)

            if 0 <= index <= 7:
                return f"trainer led {index} off"

        except (ValueError, IndexError):
            pass

    # ========================================================
    # TRAINER LED
    # ========================================================

    if "trainer" in words and "led" in words:

        try:

            led_position = words.index("led")
            number = words[led_position + 1]
            index = int(number)

            if 0 <= index <= 7:

                if "on" in words:
                    return f"trainer led {index} on"

                if "off" in words:
                    return f"trainer led {index} off"

        except (ValueError, IndexError):
            pass

    # ========================================================
    # TRAINER NUMBER WITHOUT LED
    # ========================================================

    if "trainer" in words:

        try:

            trainer_position = words.index("trainer")

            if trainer_position + 1 < len(words):

                number = words[trainer_position + 1]
                index = int(number)

                if 0 <= index <= 7:

                    if "on" in words:
                        return f"trainer led {index} on"

                    if "off" in words:
                        return f"trainer led {index} off"

        except (ValueError, IndexError):
            pass

    # ========================================================
    # TRAINER ALL
    # ========================================================

    if "trainer" in words:

        if "all" in words and "on" in words:
            return "trainer all on"

        if "all" in words and "off" in words:
            return "trainer all off"

    # ========================================================
    # BUILT-IN ARDUINO LED
    # ========================================================

    if "trainer" not in words:

        if "led" in words:

            if "on" in words:
                return "led on"

            if "off" in words:
                return "led off"

        if "arduino" in words and "on" in words:
            return "arduino on"

        if "arduino" in words and "off" in words:
            return "arduino off"

    # ========================================================
    # ALL / BOTH
    # ========================================================

    if "all" in words and "on" in words:
        return "all on"

    if "all" in words and "off" in words:
        return "all off"

    if "both" in words and "on" in words:
        return "both on"

    if "both" in words and "off" in words:
        return "both off"

    # ========================================================
    # STOP
    # ========================================================

    if "stop" in words or "halt" in words:
        return "stop"

    # ========================================================
    # STATUS
    # ========================================================

    if "status" in words:
        return "status"

    # ========================================================
    # HELP
    # ========================================================

    if "help" in words or "commands" in words:
        return "help"

    return None


# ============================================================
# PROCESS COMMAND
# ============================================================

def process_command(raw_text, source="TEXT"):

    print()
    print("========================================")
    print("[", source, "]", raw_text)
    print("========================================")

    command = normalize_command(raw_text)

    print("[Router] Normalized:", command)

    if command is None:

        print("[Router] Command not recognized.")

        return False, "Command not recognized"

    print(
        "[Router] Arduino command:",
        command
    )

    success = send_to_arduino(command)

    if success:

        print("[Router] SUCCESS")

        return True, command

    print(
        "[Router] Arduino connection failed."
    )

    return False, "Arduino connection failed"


# ============================================================
# HTTP SERVER
# ============================================================

class AMOMIIHandler(SimpleHTTPRequestHandler):

    # --------------------------------------------------------
    # CORS HEADERS
    # --------------------------------------------------------

    def end_headers(self):

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        super().end_headers()

    # --------------------------------------------------------
    # HTTP LOGGING
    # --------------------------------------------------------

    def log_message(self, format, *args):

        print(
            "[HTTP]",
            format % args
        )

    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    def do_OPTIONS(self):

        self.send_response(204)
        self.end_headers()

    # --------------------------------------------------------
    # POST
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
                "utf-8",
                errors="ignore"
            ).strip()

            print()
            print(
                "[HTTP] Received:",
                body
            )

            if not body:

                self.send_response(400)

                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
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

                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )

                self.end_headers()

                response = (
                    "OK: " + result
                ).encode("utf-8")

                self.wfile.write(response)

            else:

                self.send_response(500)

                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )

                self.end_headers()

                self.wfile.write(
                    result.encode("utf-8")
                )

        except Exception as e:

            print()
            print(
                "[HTTP ERROR]",
                e
            )

            try:

                self.send_response(500)

                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )

                self.end_headers()

                self.wfile.write(
                    b"Server error"
                )

            except:
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
    print("WEB SERVER")
    print(
        "Address:",
        f"http://{HOST}:{PORT}"
    )
    print()
    print("ARDUINO")
    print("Port:", ARDUINO_PORT)
    print("Baud:", BAUD)
    print()
    print("VOICE ROUTER: ONLINE")
    print("HTTP SERVER: ONLINE")
    print()
    print("CORS: ENABLED")
    print()
    print("========================================")
    print()
    print("Press CTRL+C to stop.")
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Stopping server...")

    finally:

        server.server_close()

        print(
            "HTTP server stopped."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if not connect_arduino():

        print(
            "WARNING: Arduino is not connected."
        )

        print(
            "The server will continue and "
            "attempt reconnects when commands arrive."
        )

    start_server()

    if arduino is not None:

        try:
            arduino.close()
        except:
            pass

        print(
            "[Arduino] Serial connection closed."
        )

    print()
    print(
        "AMOMII Command Center stopped."
    )

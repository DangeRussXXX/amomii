# ============================================================

# AMOMII ONE - COMBINED NATURAL COMMAND + WEB SERVER

# VERSION 2.1

#

# Arduino:

# COM9

# 9600 baud

#

# HTTP:

# POST /command

#

# IMPORTANT:

# This server runs on the Windows PC connected to the Arduino.

# The GitHub-hosted AMOMII page communicates with this server.

#

# CORS is enabled so the GitHub page can communicate with the

# local Arduino command server.

# ============================================================

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

```
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
```

}

# ============================================================

# ARDUINO CONNECTION

# ============================================================

arduino = None

def connect_arduino():

```
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

    # Arduino commonly resets when serial opens.
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
```

# ============================================================

# SEND COMMAND TO ARDUINO

# ============================================================

def send_to_arduino(command):

```
global arduino

# --------------------------------------------------------
# Make sure Arduino is connected
# --------------------------------------------------------

if arduino is None:

    print("[Arduino] Not connected.")
    print("[Arduino] Attempting reconnect...")

    if not connect_arduino():

        return False

try:

    print("[Arduino TX]:", command)

    # ----------------------------------------------------
    # Send command
    # ----------------------------------------------------

    arduino.write(
        (command + "\n").encode("utf-8")
    )

    arduino.flush()

    # ----------------------------------------------------
    # Give Arduino a moment to respond
    # ----------------------------------------------------

    time.sleep(0.10)

    # ----------------------------------------------------
    # Read Arduino responses
    # ----------------------------------------------------

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
```

# ============================================================

# NORMALIZE COMMAND

# ============================================================

def normalize_command(text):

```
if text is None:
    return None

# --------------------------------------------------------
# Basic cleanup
# --------------------------------------------------------

text = text.lower().strip()

text = re.sub(
    r"[.,!?]",
    "",
    text
)

# Remove common voice filler words.
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

# --------------------------------------------------------
# Convert number words to digits
# --------------------------------------------------------

words = text.split()

converted = []

for word in words:

    if word in NUMBER_WORDS:

        converted.append(
            NUMBER_WORDS[word]
        )

    else:

        converted.append(word)

words = converted

# ========================================================
# NATURAL TRAINER COMMANDS
# ========================================================

# turn on trainer led 3
# turn off trainer led 3

if (
    "turn" in words
    and "trainer" in words
    and "led" in words
):

    try:

        led_position = words.index("led")

        number = words[led_position + 1]

        index = int(number)

        if 0 <= index <= 7:

            if "on" in words:

                return (
                    f"trainer led {index} on"
                )

            if "off" in words:

                return (
                    f"trainer led {index} off"
                )

    except (ValueError, IndexError):

        pass

# ========================================================
# TRAINER LED
# ========================================================

# trainer led 0 on
# trainer led 1 off
# trainer led one on
# trainer led seven off

if (
    "trainer" in words
    and "led" in words
):

    try:

        led_position = words.index("led")

        number = words[led_position + 1]

        index = int(number)

        if 0 <= index <= 7:

            if "on" in words:

                return (
                    f"trainer led {index} on"
                )

            if "off" in words:

                return (
                    f"trainer led {index} off"
                )

    except (ValueError, IndexError):

        pass

# ========================================================
# TRAINER NUMBER WITHOUT "LED"
# ========================================================

# trainer 0 on
# trainer 7 off
# trainer one on
# trainer seven off

if "trainer" in words:

    try:

        trainer_position = words.index(
            "trainer"
        )

        if trainer_position + 1 < len(words):

            number = words[
                trainer_position + 1
            ]

            index = int(number)

            if 0 <= index <= 7:

                if "on" in words:

                    return (
                        f"trainer led {index} on"
                    )

                if "off" in words:

                    return (
                        f"trainer led {index} off"
                    )

    except (ValueError, IndexError):

        pass

# ========================================================
# TRAINER ALL
# ========================================================

if "trainer" in words:

    if (
        "all" in words
        and "on" in words
    ):

        return "trainer all on"

    if (
        "all" in words
        and "off" in words
    ):

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

    if (
        "arduino" in words
        and "on" in words
    ):

        return "arduino on"

    if (
        "arduino" in words
        and "off" in words
    ):

        return "arduino off"

# ========================================================
# BOTH / ALL
# ========================================================

if (
    "all" in words
    and "on" in words
):

    return "all on"

if (
    "all" in words
    and "off" in words
):

    return "all off"

if (
    "both" in words
    and "on" in words
):

    return "both on"

if (
    "both" in words
    and "off" in words
):

    return "both off"

# ========================================================
# STOP
# ========================================================

if (
    "stop" in words
    or "halt" in words
):

    return "stop"

# ========================================================
# STATUS
# ========================================================

if "status" in words:

    return "status"

# ========================================================
# HELP
# ========================================================

if (
    "help" in words
    or "commands" in words
):

    return "help"

# ========================================================
# UNKNOWN
# ========================================================

return None
```

# ============================================================

# PROCESS COMMAND

# ============================================================

def process_command(raw_text, source="TEXT"):

```
print()
print("========================================")
print("[", source, "]", raw_text)
print("========================================")

command = normalize_command(
    raw_text
)

print("[Router] Normalized:", command)

if command is None:

    print(
        "[Router] Command not recognized."
    )

    return False, "Command not recognized"

print(
    "[Router] Arduino command:",
    command
)

success = send_to_arduino(
    command
)

if success:

    print(
        "[Router] SUCCESS"
    )

    return True, command

print(
    "[Router] Arduino connection failed."
)

return False, "Arduino connection failed"
```

# ============================================================

# HTTP SERVER

# ============================================================

class AMOMIIHandler(
SimpleHTTPRequestHandler
):

```
# --------------------------------------------------------
# CORS HEADERS
# --------------------------------------------------------

def send_cors_headers(self):

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

# --------------------------------------------------------
# Cleaner HTTP logging
# --------------------------------------------------------

def log_message(
    self,
    format,
    *args
):

    print(
        "[HTTP]",
        format % args
    )

# --------------------------------------------------------
# OPTIONS
#
# Browser sends this before the POST when CORS
# requires a preflight request.
# --------------------------------------------------------

def do_OPTIONS(self):

    self.send_response(204)

    self.send_cors_headers()

    self.end_headers()

# --------------------------------------------------------
# POST
# --------------------------------------------------------

def do_POST(self):

    try:

        # ------------------------------------------------
        # CORS
        # ------------------------------------------------

        # The response must explicitly allow the
        # GitHub-hosted page to access this server.

        # ------------------------------------------------
        # Get content length
        # ------------------------------------------------

        length = int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        # ------------------------------------------------
        # Read body
        # ------------------------------------------------

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

        # ------------------------------------------------
        # Empty request
        # ------------------------------------------------

        if not body:

            self.send_response(400)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_cors_headers()

            self.end_headers()

            self.wfile.write(
                b"Empty command"
            )

            return

        # ------------------------------------------------
        # Process command
        # ------------------------------------------------

        success, result = process_command(
            body,
            "VOICE/HTTP"
        )

        # ------------------------------------------------
        # Successful response
        # ------------------------------------------------

        if success:

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_cors_headers()

            self.end_headers()

            response = (
                "OK: " + result
            ).encode("utf-8")

            self.wfile.write(
                response
            )

            return

        # ------------------------------------------------
        # Command/Arduino failure
        # ------------------------------------------------

        self.send_response(500)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.send_cors_headers()

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

            self.send_cors_headers()

            self.end_headers()

            self.wfile.write(
                b"Server error"
            )

        except:

            pass
```

# ============================================================

# START SERVER

# ============================================================

def start_server():

```
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

print("CORS: ENABLED")
print("VOICE ROUTER: ONLINE")
print("HTTP SERVER: ONLINE")

print()

print("========================================")
print()

print("Examples:")
print()

print("  led on")
print("  led off")

print()

print("  trainer led 0 on")
print("  trainer led 0 off")

print()

print("  trainer led three on")
print("  trainer led seven off")

print()

print("  trainer 0 on")
print("  trainer 7 off")

print()

print("  turn on trainer led three")
print("  turn off trainer led seven")

print()

print("  trainer all on")
print("  trainer all off")

print()

print("  all on")
print("  all off")

print()

print("  both on")
print("  both off")

print()

print("Type commands below.")
print("Press CTRL+C to stop.")
print()

# --------------------------------------------------------
# Run server
# --------------------------------------------------------

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
```

# ============================================================

# MAIN

# ============================================================

if **name** == "**main**":

```
# --------------------------------------------------------
# Connect Arduino FIRST
# --------------------------------------------------------

if not connect_arduino():

    print(
        "WARNING: Arduino is not connected."
    )

    print(
        "The server will continue and "
        "attempt reconnects when commands arrive."
    )

# --------------------------------------------------------
# Start HTTP server
# --------------------------------------------------------

start_server()

# --------------------------------------------------------
# Cleanup
# --------------------------------------------------------

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

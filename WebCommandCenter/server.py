from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import serial

HOST = "127.0.0.1"
PORT = 8000

class AMOMIIHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")

    # ⭐ NEW: Voice command endpoint
    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length).decode().strip()

        print("[VOICE] Received:", body)

        # Normalize voice text
        cmd = body.lower().replace(" ", "")
        word_map = {
            "zero": "0", "one": "1", "two": "2", "three": "3",
            "four": "4", "five": "5", "six": "6", "seven": "7",
            "eight": "8", "nine": "9", "oh": "0"
        }
        for word, digit in word_map.items():
            cmd = cmd.replace(word, digit)

        print("[Router] Sending:", cmd)

        # Send to Arduino
        try:
            arduino = serial.Serial("COM3", 9600, timeout=1)
            arduino.write((cmd + "\n").encode())
            arduino.close()
        except Exception as e:
            print("[ERROR] Could not send to Arduino:", e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


server = ThreadingHTTPServer(
    (HOST, PORT),
    AMOMIIHandler
)

print()
print("========================================")
print("       DANGERUSS WEB COMMAND CENTER")
print("========================================")
print()
print(f"Server: http://{HOST}:{PORT}")
print()
print("Press CTRL+C to stop the server.")
print()

try:
    server.serve_forever()

except KeyboardInterrupt:
    print("\nStopping AMOMII server...")

finally:
    server.server_close()
    print("Server stopped.")

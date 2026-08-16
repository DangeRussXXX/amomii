from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 8000


class AMOMIIHandler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")


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
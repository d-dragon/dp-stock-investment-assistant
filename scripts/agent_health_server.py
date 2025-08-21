import threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *a): return

def warm_agent():
    # Placeholder: warm caches / models as needed
    time.sleep(0.5)

if __name__ == "__main__":
    warm_agent()
    server = HTTPServer(("0.0.0.0", 7000), Handler)
    print("Agent worker ready on :7000")
    server.serve_forever()
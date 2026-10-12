import os
import sys
import json
import base64
import time
import tempfile
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# ============================================================
# PROJECT ROOT SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import LangGraph workflow
try:
    from graph.workflow import build_workflow
    print("[SERVER] Compiling LangGraph workflow...")
    workflow_app = build_workflow()
    print("[SERVER] LangGraph workflow compiled successfully.")
except Exception as e:
    print(f"[SERVER WARNING] Could not compile workflow on startup: {e}")
    workflow_app = None

TEMP_DIR = PROJECT_ROOT / "temp_uploads"
TEMP_DIR.mkdir(exist_ok=True)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True


class LoobVisionHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # Serve static files from 'public' folder if present, else project root
        public_dir = PROJECT_ROOT / "public"
        if public_dir.exists():
            super().__init__(*args, directory=str(public_dir), **kwargs)
        else:
            super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/api/status" or self.path == "/api/health":
            self.send_json_response({
                "status": "ready",
                "model": "Original Image Model",
                "backend_ready": workflow_app is not None
            })
            return

        # Serve static index.html or assets
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/analyze" or self.path == "/analyze":
            self.handle_analyze()
            return

        self.send_error(404, "Endpoint not found")

    def handle_analyze(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8"))
            image_data = payload.get("image", "")

            if not image_data:
                self.send_json_response({"error": "No image data provided"}, status_code=400)
                return

            # Extract base64 payload if data URL
            if "," in image_data:
                header, encoded = image_data.split(",", 1)
            else:
                encoded = image_data

            image_bytes = base64.b64decode(encoded)

            # Write to temporary file
            temp_file = TEMP_DIR / f"capture_{int(time.time() * 1000)}.png"
            with open(temp_file, "wb") as f:
                f.write(image_bytes)

            print(f"[SERVER] Processing analysis for image: {temp_file}")

            # Invoke existing backend LangGraph workflow
            if workflow_app is None:
                from graph.workflow import build_workflow
                app = build_workflow()
            else:
                app = workflow_app

            initial_state = {"image_path": str(temp_file)}
            result = app.invoke(initial_state)

            # Clean up temp image
            try:
                temp_file.unlink()
            except Exception:
                pass

            # Standardize output for response
            response_data = dict(result)
            self.send_json_response(response_data)

        except Exception as e:
            print(f"[SERVER ERROR] Analysis failed: {e}")
            self.send_json_response({
                "error": f"Analysis failed: {str(e)}"
            }, status_code=500)

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def run_server(port=8000):
    server_address = ("", port)
    httpd = ThreadedHTTPServer(server_address, LoobVisionHandler)
    print(f"[SERVER] LOOB VISION AI Server running at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)

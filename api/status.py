import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import LoobVisionHandler, workflow_app

class handler(LoobVisionHandler):
    """Vercel serverless function entrypoint for /api/status"""
    def do_GET(self):
        self.send_json_response({
            "status": "ready",
            "model": "Original Image Model",
            "backend_ready": workflow_app is not None
        })

    def do_POST(self):
        self.send_json_response({
            "status": "ready",
            "model": "Original Image Model",
            "backend_ready": workflow_app is not None
        })

app = handler

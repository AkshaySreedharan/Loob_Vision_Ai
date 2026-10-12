import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import LoobVisionHandler

class handler(LoobVisionHandler):
    """Vercel serverless function entrypoint for /api/report and /api/report/pdf"""
    pass

app = handler

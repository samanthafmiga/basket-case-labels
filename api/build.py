"""
Vercel Python serverless function — POST /api/build
Body (JSON): { productName, ingredients, price, allergens? }
Response: application/pdf
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the project root to sys.path so `lib.label_renderer` imports cleanly.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from lib.label_renderer import build_sheet_bytes, safe_filename


class handler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(raw or "{}")
        except Exception as e:
            self._error(400, f"Bad JSON: {e}")
            return

        product = (body.get("productName") or "").strip()
        ingredients = (body.get("ingredients") or "").strip()
        price = (body.get("price") or "").strip()
        allergens = (body.get("allergens") or "").strip()

        if not product:
            return self._error(400, "productName is required")
        if not ingredients:
            return self._error(400, "ingredients is required")

        try:
            pdf = build_sheet_bytes(product, ingredients, price, allergens)
        except Exception as e:
            return self._error(500, f"Render failed: {e}")

        filename = f"Basket_Case_Labels_{safe_filename(product.upper())}.pdf"
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"',
        )
        self.send_header("Content-Length", str(len(pdf)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(pdf)

    def _error(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._set_cors()
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode("utf-8"))

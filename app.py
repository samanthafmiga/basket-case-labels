"""
Basket Case Labels — Vercel Python entrypoint (Flask app).
GET  /                          → form UI (index.html)
GET  /basket-case-labels.skill  → download installable skill bundle
POST /api/build                 → JSON {productName, ingredients, price, allergens?} → PDF download
"""
import io
import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file

# Make `lib.label_renderer` importable
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from lib.label_renderer import build_sheet_bytes, safe_filename, audit_label_content
from lib import kv_store

app = Flask(__name__, static_folder=None)

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(_ROOT, "index.html")

@app.route("/basket-case-labels.skill", methods=["GET"])
def download_skill():
    return send_from_directory(
        _ROOT,
        "basket-case-labels.skill",
        mimetype="application/zip",
        as_attachment=True,
        download_name="basket-case-labels.skill",
    )

@app.route("/api/preview", methods=["POST"])
def api_preview():
    body = request.get_json(silent=True) or {}
    product = (body.get("productName") or "").strip()
    ingredients = (body.get("ingredients") or "").strip()
    price = (body.get("price") or "").strip()
    allergens = (body.get("allergens") or "").strip()
    if not product or not ingredients:
        return jsonify({"fits": True, "empty": True})
    try:
        audit = audit_label_content(product, ingredients, price, allergens)
    except Exception as e:
        return jsonify({"error": f"Audit failed: {e}"}), 500
    return jsonify(audit)


@app.route("/api/labels", methods=["GET"])
def api_labels():
    return jsonify({"labels": kv_store.get_labels(), "kvEnabled": kv_store.kv_enabled()})


@app.route("/api/build", methods=["POST"])
def api_build():
    body = request.get_json(silent=True) or {}
    product = (body.get("productName") or "").strip()
    ingredients = (body.get("ingredients") or "").strip()
    price = (body.get("price") or "").strip()
    allergens = (body.get("allergens") or "").strip()
    raw_count = body.get("count", 9)
    try:
        count = max(1, min(99, int(raw_count)))
    except (TypeError, ValueError):
        count = 9
    if not product:
        return jsonify({"error": "productName is required"}), 400
    if not ingredients:
        return jsonify({"error": "ingredients is required"}), 400
    try:
        pdf = build_sheet_bytes(product, ingredients, price, allergens, count=count)
    except Exception as e:
        return jsonify({"error": f"Render failed: {e}"}), 500
    # Auto-save to the shared label repository so future builds can recall it.
    try:
        kv_store.add_label({
            "productName": product,
            "ingredients": ingredients,
            "price": price,
            "allergens": allergens,
        })
    except Exception:
        pass  # Never let a save failure block the download.

    fname = f"Basket_Case_Labels_{safe_filename(product.upper())}.pdf"
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=fname,
    )

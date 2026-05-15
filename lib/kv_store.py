"""
Tiny wrapper around Vercel KV (Upstash Redis REST API).

Reads env vars KV_REST_API_URL and KV_REST_API_TOKEN (auto-injected by Vercel
when KV is connected to the project). If those env vars are absent or the
network call fails, get_labels() returns the SEED list so the UI is still
useful — only persistence of new additions across requests is lost.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

KV_URL = os.environ.get("KV_REST_API_URL", "").rstrip("/")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN", "")
LABELS_KEY = "labels:all"
MAX_LABELS = 200

# Seed list — extracted from Sam's existing PDFs in Downloads/Basket Case Labels.
# Always available as fallback / starting state when KV is empty.
SEED_LABELS = [
    {"productName": "Avocado Potato Salad",
     "ingredients": "Cayenne Potato, Avocado, Lime, Red Onion, Green Onion, Egg, Mayo",
     "price": "$8", "allergens": ""},
    {"productName": "Boursin Grapes",
     "ingredients": "Green Grapes, Prosciutto, Milk, Garlic, Pepper, Parsley, Chives",
     "price": "$9", "allergens": ""},
    {"productName": "Caprese Pasta Salad",
     "ingredients": "Orzo, Cherry Tomato, Fresh Mozzarella, Basil Pesto, Balsamic, Olive Oil, Salt, Pepper",
     "price": "$9", "allergens": ""},
    {"productName": "Charred Lemon and Parsley Potato Salad",
     "ingredients": "Potato, Dijon, Parsley, Lemon, Olive Oil, Garlic, Capers, Salt, Pepper",
     "price": "", "allergens": ""},
    {"productName": "Chicken Quinoa Meatballs",
     "ingredients": "Chicken, Quinoa, Garlic, Onion, Salt, Pepper, Oregano, Pesto (Basil, Lemon, Garlic, Pistachio, Olive Oil, Cashew), Egg",
     "price": "$10", "allergens": ""},
    {"productName": "Chicken Salad",
     "ingredients": "Chicken, Grapes, Candied Walnut, Greek Yogurt, Sugar, Lemon, Mayo, Oregano, Mustard, Cayenne, Green Onion, Salt, Pepper",
     "price": "$8", "allergens": ""},
    {"productName": "Fresh Cut Mango",
     "ingredients": "Mango",
     "price": "$5", "allergens": ""},
    {"productName": "Pink Pineapple",
     "ingredients": "Pink pineapple",
     "price": "$3.99", "allergens": ""},
    {"productName": "Strawberry Bites",
     "ingredients": "Strawberry, Cream Cheese, Butter, Sugar, Vanilla, Biscoff",
     "price": "$10", "allergens": ""},
]


def kv_enabled() -> bool:
    return bool(KV_URL and KV_TOKEN)


def _req(path: str, *, method: str = "POST", body: bytes | None = None) -> dict | None:
    if not kv_enabled():
        return None
    url = f"{KV_URL}/{path}"
    req = urllib.request.Request(url, method=method, data=body)
    req.add_header("Authorization", f"Bearer {KV_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def _stored_labels() -> list[dict] | None:
    """Return labels list from KV, or None if unreachable / unset."""
    res = _req(f"get/{LABELS_KEY}", method="GET")
    if not res:
        return None
    raw = res.get("result")
    if raw in (None, ""):
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else None
    except (json.JSONDecodeError, TypeError):
        return None


def get_labels() -> list[dict]:
    """Return labels list — KV-stored if present, otherwise the seed list."""
    stored = _stored_labels()
    if stored is None:
        return list(SEED_LABELS)
    return stored


def _set_labels(labels: list[dict]) -> bool:
    payload = json.dumps(labels).encode()
    res = _req(f"set/{LABELS_KEY}", method="POST", body=payload)
    return bool(res and res.get("result") == "OK")


def add_label(label: dict) -> list[dict]:
    """Insert/update a label. Dedup by product name (case-insensitive).
    Returns the updated list (whether or not KV is reachable)."""
    name = (label.get("productName") or "").strip()
    if not name:
        return get_labels()
    key = name.lower()
    stored = _stored_labels()
    base = stored if stored is not None else list(SEED_LABELS)
    filtered = [l for l in base if (l.get("productName") or "").strip().lower() != key]
    filtered.insert(0, label)
    filtered = filtered[:MAX_LABELS]
    _set_labels(filtered)
    return filtered

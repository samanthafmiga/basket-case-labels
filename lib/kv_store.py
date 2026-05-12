"""
Tiny wrapper around Vercel KV (Upstash Redis REST API).

Reads env vars KV_REST_API_URL and KV_REST_API_TOKEN (auto-injected by Vercel
when KV is connected to the project). If those env vars are absent, all
operations degrade to the in-memory seed only — the app keeps working but
nothing persists across requests.
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
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def get_labels() -> list[dict]:
    """Return the list of saved labels (most recent first). Empty if KV down."""
    res = _req(f"get/{LABELS_KEY}", method="GET")
    if not res or res.get("result") in (None, ""):
        return []
    try:
        data = json.loads(res["result"])
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def set_labels(labels: list[dict]) -> bool:
    """Overwrite the saved label list."""
    payload = json.dumps(labels).encode()
    res = _req(f"set/{LABELS_KEY}", method="POST", body=payload)
    return bool(res and res.get("result") == "OK")


def add_label(label: dict) -> list[dict]:
    """Insert/update a label. Dedup by product name (case-insensitive)."""
    name = (label.get("productName") or "").strip()
    if not name:
        return get_labels()
    key = name.lower()
    existing = get_labels()
    filtered = [l for l in existing if (l.get("productName") or "").strip().lower() != key]
    filtered.insert(0, label)
    filtered = filtered[:MAX_LABELS]
    if set_labels(filtered):
        return filtered
    return existing

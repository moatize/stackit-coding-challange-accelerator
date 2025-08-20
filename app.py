from __future__ import annotations
from flask import Flask, request, jsonify
import requests
from typing import Any, Dict, List

# Konfiguration Messenger
NTFY_BASE_URL = "https://ntfy.sonrio.eu"
NTFY_TOPIC = "stackit-challenge"
NTFY_URL = f"https://ntfy.sonrio.eu/stackit-challenge"

# In-Memory-Speicher
NOTIFICATIONS: List[Dict[str, Any]] = []

# Flask-App
app = Flask(__name__)

# Prüfung Felder & Type
def _validate_payload(data: Dict[str, Any]) -> tuple[bool, str]:
    required = ("Type", "Name", "Description")
    for key in required:
        if key not in data:
            return False, f"Missing field: {key}"
        if not isinstance(data[key], str) or not data[key].strip():
            return False, f"Field must be non-empty string: {key}"
    if data["Type"] not in ("Warning", "Info"):
        return False, 'Unsupported "Type" (allowed: "Warning", "Info")'
    return True, ""

# Weiterleitung von "Warning" an ntfy 
def _forward_to_ntfy(notification: Dict[str, Any]) -> bool:
    text = f"[{notification['Type']}] {notification['Name']}\n{notification['Description']}"
    headers = {"Title": f"Warning: {notification['Name']}"}
    try:
        resp = requests.post(NTFY_URL, data=text.encode("utf-8"), headers=headers, timeout=5)
        return 200 <= resp.status_code < 300
    except requests.RequestException:
        return False

# Endpoint (EMpfangen, Validieren & Weiterleiten)
@app.post("/notifications")
def receive_notification():
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "Malformed JSON"}), 400

    ok, msg = _validate_payload(data)
    if not ok:
        return jsonify({"error": msg}), 400

    # Anlegen neuer Benachrichtigung
    notification = {
        "Type": data["Type"],
        "Name": data["Name"],
        "Description": data["Description"],
        "forwarded": False,
    }

    # Weiterleitung bei "Warning"
    if data["Type"] == "Warning":
        forwarded = _forward_to_ntfy(notification)
        notification["forwarded"] = bool(forwarded)
        NOTIFICATIONS.append(notification)
        if forwarded:
            return jsonify({"status": "forwarded"}), 202
        else:
            return jsonify({"status": "forwarding_failed"}), 502

    # sonst: nur speichern, keine Weiterleitung
    NOTIFICATIONS.append(notification)
    return jsonify({"status": "ignored"}), 200


if __name__ == "__main__":
    # Minimaler Dev-Server start (kein WSGI/Proxy, da nicht gefordert)
    app.run(host="127.0.0.1", port=5000, debug=False)



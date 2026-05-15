import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g, jsonify
from flask_cors import CORS
from time import time

# ensure logs directory exists (relative to project root)
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "backend.log")

# console logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")

# rotating file handler
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logging.getLogger().addHandler(file_handler)

# create Flask app if not already created
app = globals().get("app") or Flask(__name__)
CORS(app)

app.logger.info("Backend starting up")

@app.before_request
def start_timer():
    g.start_time = time()
    try:
        body = request.get_json(silent=True)
    except Exception:
        body = None
    if isinstance(body, dict):
        for k in ("password", "token", "ssn", "medical_record"):
            if k in body:
                body[k] = "[REDACTED]"
    app.logger.info("Request start: %s %s from %s body=%s", request.method, request.path, request.remote_addr, body)

@app.after_request
def log_response(response):
    duration = (time() - getattr(g, "start_time", time())) * 1000
    app.logger.info("Request end: %s %s status=%s duration=%.1fms", request.method, request.path, response.status_code, duration)
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception("Unhandled exception during request")
    raise

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid JSON. Send application/json with a valid JSON body."}, 400

    message = data.get("message", "")
    reply = f"I heard: {message}"
    possible_conditions = ["Infection"] if "fever" in message.lower() else []
    preventive_tip = "Rest, hydrate, monitor symptoms." if possible_conditions else ""
    safety_note = "Seek emergency care if chest pain or difficulty breathing." if "chest pain" in message.lower() else ""
    return jsonify({
        "reply": reply,
        "possible_conditions": possible_conditions,
        "preventive_tip": preventive_tip,
        "safety_note": safety_note
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
@app.route("/health", methods=["GET"])
def health():
    return {"status":"ok"}, 200

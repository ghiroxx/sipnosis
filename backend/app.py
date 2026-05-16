import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from oracle_engine import generate_oracle
from vision_oracle import analyze_stain_image

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/health", methods=["GET"])
def healthcheck():
    return jsonify({
        "status": "ok",
        "service": "sipnosis-backend",
        "version": "phase-1-architecture",
    })


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "service": "sipnosis-backend",
    })


@app.route("/api/oracle", methods=["POST"])
def oracle():
    file = request.files.get("file")
    intent = request.form.get("intent", "direzione")
    question = request.form.get("question", "")

    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    filename = secure_filename(file.filename or "oracle-image.jpg")
    filepath = UPLOAD_DIR / filename

    file.save(filepath)

    oracle_result = generate_oracle(intent, filename, question)
    vision_result = analyze_stain_image(filepath, intent, question)

    parsed_vision = None

    if vision_result.get("enabled") and vision_result.get("content"):
        try:
            parsed_vision = json.loads(vision_result["content"])
        except Exception:
            parsed_vision = {
                "raw": vision_result["content"]
            }

    return jsonify({
        "success": True,
        "oracle": oracle_result,
        "vision": parsed_vision,
        "vision_enabled": vision_result.get("enabled", False),
        "image": filename,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

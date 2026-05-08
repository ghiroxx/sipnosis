import base64
import json
import os
from datetime import datetime

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

READINGS = {
    "direzione": "La forma indica una soglia. Il passo giusto è piccolo, preciso e verificabile.",
    "protezione": "Il segno chiede confini chiari. Non tutto deve essere aperto, spiegato o condiviso.",
    "abbondanza": "L'abbondanza qui è flusso ordinato: ciò che entra deve poter circolare e ritornare.",
    "relazione": "Due correnti si osservano. Serve chiarezza prima della fusione.",
    "trasformazione": "La macchia parla di mutazione lenta. Una forma vecchia sta già lasciando spazio.",
}

SYMBOLS = ["ankh", "spirale", "occhio", "soglia", "ruota"]


def _json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def _fallback_oracle(intent, question, image_size):
    normalized = intent if intent in READINGS else "direzione"
    seed = len(question or "") + int(image_size or 0) + datetime.utcnow().day
    return {
        "intent": normalized,
        "symbol": SYMBOLS[seed % len(SYMBOLS)],
        "reading": READINGS[normalized],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def _vision_oracle(image_bytes, intent, question):
    if OpenAI is None or not os.getenv("OPENAI_API_KEY"):
        return None

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are SipnoSis, a symbolic oracle interpreting coffee or tea stains. "
                    "Return only JSON with: symbol, mood, interpretation. "
                    "Keep the interpretation poetic, grounded, and concise."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Intent: {intent}\nQuestion: {question}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    },
                ],
            },
        ],
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"raw": response.choices[0].message.content}


class handler:
    def __init__(self, req, res):
        self.req = req
        self.res = res

    def do_OPTIONS(self):
        _json_response(self, {"ok": True})

    def do_POST(self):
        # Vercel Python runtime exposes the raw request body through rfile.
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else b""
        content_type = self.headers.get("Content-Type", "")

        # Minimal endpoint: accepts raw image body or multipart payload.
        # The static frontend sends multipart; this endpoint still returns a stable oracle
        # even if multipart parsing is not available in the serverless runtime.
        intent = "direzione"
        question = ""

        oracle = _fallback_oracle(intent, question, len(body))
        vision = None

        if body and "image" in content_type:
            try:
                vision = _vision_oracle(body, intent, question)
            except Exception as exc:
                vision = {"error": str(exc)}

        _json_response(self, {
            "success": True,
            "oracle": oracle,
            "vision": vision,
            "vision_enabled": bool(vision and "error" not in vision),
            "runtime": "vercel-serverless",
        })

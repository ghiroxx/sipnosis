import base64
import json
import os
from datetime import datetime
from urllib.parse import unquote

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

INTENTS = {
    "direzione": {
        "pressure": "orientamento",
        "gesture": "Scegli un gesto piccolo e verificabile. Non aggiungere un secondo compito finché il primo non è compiuto.",
    },
    "protezione": {
        "pressure": "confine",
        "gesture": "Non spiegare una decisione più di una volta. Se il confine è chiaro, ripeterlo lo indebolisce.",
    },
    "abbondanza": {
        "pressure": "circolazione",
        "gesture": "Libera una cosa trattenuta: denaro, oggetto, messaggio o promessa. L’accumulo fermo diventa peso.",
    },
    "relazione": {
        "pressure": "distanza",
        "gesture": "Scrivi la frase che eviti di dire. Non inviarla subito: prima osserva cosa ti costringe a nascondere.",
    },
    "trasformazione": {
        "pressure": "mutazione",
        "gesture": "Rimuovi un’abitudine piccola ma ripetuta. La trasformazione inizia dove la ripetizione perde autorità.",
    },
}

FORMS = [
    {
        "symbol": "soglia interrotta",
        "observation": "Una massa compatta sembra aprirsi solo in un punto, come se il passaggio fosse stato trattenuto.",
        "motion": "Il movimento non è libero: procede, si ferma, poi cerca una seconda uscita.",
        "tension": "Qualcosa dentro di te ha già scelto, ma la struttura esterna continua a chiedere conferme.",
        "warning": "Il ritardo non protegge più: conserva la forma vecchia.",
        "oracle_line": "La soglia non si apre per forza, ma per precisione.",
    },
    {
        "symbol": "spirale chiusa",
        "observation": "Il segno tende a richiudersi su se stesso, lasciando una pressione più scura verso il centro.",
        "motion": "La macchia non indica avanzamento lineare: indica ritorno, ripetizione, controllo.",
        "tension": "Stai tornando allo stesso punto con parole diverse. La domanda non è nuova: è solo rimasta incompleta.",
        "warning": "Ripetere l’analisi può diventare una forma elegante di immobilità.",
        "oracle_line": "Il cerchio diventa gabbia quando dimentica l’uscita.",
    },
    {
        "symbol": "frattura ascendente",
        "observation": "Una linea o apertura sottile sale dal corpo della macchia verso una zona più chiara.",
        "motion": "Il movimento cerca aria: qualcosa tenta di uscire dalla densità senza distruggerla.",
        "tension": "Una parte di te vuole alleggerire, ma teme che semplificare significhi perdere valore.",
        "warning": "Non tutto ciò che è pesante è profondo.",
        "oracle_line": "La crepa appare dove la verità cerca respiro.",
    },
    {
        "symbol": "isola scura",
        "observation": "Un nucleo isolato resta separato dal resto del campo, più denso e meno disponibile alla lettura.",
        "motion": "La macchia trattiene un punto non risolto: non si espande, non scompare, rimane.",
        "tension": "C’è un tema che continui a tenere fuori dal discorso principale, ma che organizza il resto da lontano.",
        "warning": "Ciò che viene isolato non perde forza: diventa centro nascosto.",
        "oracle_line": "L’isola parla proprio perché non si collega.",
    },
    {
        "symbol": "ramo diviso",
        "observation": "La forma si biforca: due direzioni nascono dallo stesso deposito.",
        "motion": "Non appare conflitto violento, ma una scelta di orientamento: la stessa energia non può servire due fini opposti.",
        "tension": "Vuoi mantenere possibilità aperte, ma la dispersione sta già chiedendo un prezzo.",
        "warning": "Tenere entrambe le vie può impedire a una sola di diventare reale.",
        "oracle_line": "Il ramo sceglie crescendo, non pensando.",
    },
]


def _json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type, X-Sipnosis-Intent, X-Sipnosis-Question",
    )
    handler.end_headers()
    handler.wfile.write(body)


def _normalise_intent(value):
    value = (value or "direzione").strip().lower()
    return value if value in INTENTS else "direzione"


def _build_reading(intent, question, image_size, vision=None):
    normalized = _normalise_intent(intent)
    seed = len(question or "") + int(image_size or 0) + datetime.utcnow().day
    form = FORMS[seed % len(FORMS)]
    intent_data = INTENTS[normalized]

    visual_observation = form["observation"]
    symbolic_motion = form["motion"]
    symbol = form["symbol"]

    if isinstance(vision, dict):
        visual_observation = vision.get("visual_observation") or vision.get("observation") or visual_observation
        symbolic_motion = vision.get("symbolic_motion") or vision.get("motion") or symbolic_motion
        symbol = vision.get("symbol") or symbol

    reading = {
        "intent": normalized,
        "pressure": intent_data["pressure"],
        "symbol": symbol,
        "visual_observation": visual_observation,
        "symbolic_motion": symbolic_motion,
        "psychological_tension": form["tension"],
        "warning": form["warning"],
        "ritual_gesture": intent_data["gesture"],
        "oracle_line": form["oracle_line"],
        "reading": (
            f"{visual_observation}\n\n"
            f"{symbolic_motion}\n\n"
            f"{form['tension']}\n\n"
            f"Pressione dominante: {intent_data['pressure']}.\n"
            f"Avvertimento: {form['warning']}\n"
            f"Gesto rituale: {intent_data['gesture']}\n\n"
            f"{form['oracle_line']}"
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if question:
        reading["question_reflection"] = (
            "La domanda non viene trattata come predizione, ma come pressione che ha orientato la macchia."
        )

    return reading


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
                    "You are SipnoSis, a disciplined stain-reading oracle. "
                    "You read ONLY coffee, tea, or liquid residue stains. "
                    "Do not read tarot, astrology, numerology, faces, palms, dreams, or general fortune telling. "
                    "Treat the stain as a spatial symbolic field. First observe visible form, density, motion, openings, clusters, voids, and direction. "
                    "Do not overclaim. If the image is unclear, say the stain refuses clarity. "
                    "Avoid generic spiritual language: no universe, vibrations, manifesting, love and light, destiny, or vague positivity. "
                    "Return only JSON with these keys: symbol, visual_observation, symbolic_motion, mood. "
                    "Write in Italian. Keep it precise, restrained, and grounded in the visible stain."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Intento: {intent}\nDomanda: {question}"},
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
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else b""
        content_type = self.headers.get("Content-Type", "")

        intent = _normalise_intent(self.headers.get("X-Sipnosis-Intent", "direzione"))
        question = unquote(self.headers.get("X-Sipnosis-Question", "")).strip()

        vision = None
        if body and "image" in content_type:
            try:
                vision = _vision_oracle(body, intent, question)
            except Exception as exc:
                vision = {"error": str(exc)}

        oracle = _build_reading(intent, question, len(body), vision if isinstance(vision, dict) else None)

        _json_response(self, {
            "success": True,
            "oracle": oracle,
            "vision": vision,
            "vision_enabled": bool(vision and isinstance(vision, dict) and "error" not in vision),
            "runtime": "vercel-serverless",
            "doctrine": "stain-reading-only-v1",
        })

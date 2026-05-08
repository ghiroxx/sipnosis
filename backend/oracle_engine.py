from datetime import datetime

READINGS = {
    "direzione": [
        "La macchia mostra una soglia. Il movimento corretto è preciso, non impulsivo.",
        "Un cambiamento piccolo ma continuo avrà più effetto di una rottura improvvisa.",
    ],
    "protezione": [
        "Conserva energia e riduci dispersione. Qualcosa richiede contenimento.",
        "Il simbolo indica confini: non tutto deve essere accessibile a tutti.",
    ],
    "abbondanza": [
        "L’energia si muove verso apertura e ritorno. L’abbondanza nasce da circolazione ordinata.",
        "Un gesto concreto porterà più risultato di una lunga attesa.",
    ],
    "relazione": [
        "Due direzioni si stanno osservando ma non coincidono ancora.",
        "La chiarezza emotiva sarà più utile della seduzione simbolica.",
    ],
    "trasformazione": [
        "Il segno parla di mutazione lenta. Una forma vecchia sta perdendo struttura.",
        "La trasformazione è già iniziata prima che tu la riconoscessi.",
    ],
}

SYMBOLS = ["ankh", "spirale", "occhio", "soglia", "ruota"]


def generate_oracle(intent: str, image_name: str, question: str = ""):
    normalized = (intent or "direzione").strip().lower()

    if normalized not in READINGS:
        normalized = "direzione"

    seed = len(image_name or "") + len(question or "") + datetime.utcnow().day

    readings = READINGS[normalized]
    symbol = SYMBOLS[seed % len(SYMBOLS)]
    reading = readings[seed % len(readings)]

    return {
        "intent": normalized,
        "symbol": symbol,
        "reading": reading,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

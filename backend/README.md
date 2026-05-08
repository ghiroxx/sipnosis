# SipnoSis Backend

Backend Flask per il progetto SipnoSis.

## Endpoint

### GET /ping
Verifica stato backend.

### POST /api/oracle
Riceve:
- immagine (`file`)
- intento (`intent`)
- domanda rituale (`question`)

Restituisce:
- simbolo
- lettura
- timestamp

## Avvio locale

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Struttura

```text
backend/
├── app.py
├── oracle_engine.py
├── requirements.txt
├── uploads/
└── .env.example
```

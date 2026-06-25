# SipnoSis

SipnoSis is a static-first Vercel project for symbolic coffee/tea stain readings, with a small serverless oracle API foundation and a new Cognitive Bridge MVP route.

## Live routes

- `/` — SipnoSis cup/stain reading interface
- `/bridge/` — Cognitive Bridge landing page
- `/bridge/clarify/` — paste confusing text and generate a 3-step action card
- `/bridge/result/` — view, copy and locally save the latest action card

## Current deployment structure

The Vercel project can safely use Root Directory:

```text
frontend
```

The expected repository structure is:

```text
sipnosis/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vercel.json
│   ├── api/
│   │   └── oracle.py
│   └── bridge/
│       ├── index.html
│       ├── clarify/
│       │   └── index.html
│       └── result/
│           └── index.html
├── backend/
└── README.md
```

## Build

From `frontend/`:

```bash
pnpm install
pnpm run build
```

The build command creates `dist/`, copies the SipnoSis landing page and copies the Cognitive Bridge static routes.

## Cognitive Bridge MVP

Cognitive Bridge turns confusing text into:

1. Goal
2. Next 3 steps
3. Ready message
4. Risk level
5. Needs approval flag
6. Source-based explanation

This first MVP is intentionally draft-only. It does not send, submit, sign, pay, automate browsers or act on behalf of the user. High-risk matters are flagged for review.

## Notes

- SipnoSis AI vision requires `OPENAI_API_KEY` in the correct production Vercel project.
- Cognitive Bridge currently runs client-side and stores recent cards only in browser localStorage.
- Browser automation, Supabase persistence and real AI classification should come after the manual-paste MVP is tested with real examples.

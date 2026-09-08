# Anew — Nudger sub app

Anew collects and summarizes news with two perspectives. Nudger Core owns users, subscriptions, delivery policy, and FCM; Anew never receives device tokens.

## Contract

`POST /api/nudger/v1/evaluate`, `Authorization: Bearer <NUDGER_SERVICE_TOKEN>` (32+ characters).

Request: `{"request_id":"job-uuid","evaluated_at":<Unix seconds>,"settings":{"schema_version":1,"keywords":["AI"],"max_items":3}}`.

Response: `status: no_content` when no fresh matching news, otherwise `notification` with stable `source_event_id`, title, body, expires_at, and `content.summary_items`. Database failures return 503. Invalid settings return 422. Each summary expires after 24 hours. Missing keyword matches never produce synthetic news. Nudger polls this endpoint; polling does not invoke Gemini.

## Run

Copy `.env.example` to `.env`, set MongoDB URI, service token, and Google API key. Run `pip install -r app/requirements.lock` and `cd app && uvicorn main:app --port 8001`. Existing React `/api/data` remains supported; static files are optional for a backend-only checkout.

Run one separate collector with `cd app && python -m collector`. Production rejects an embedded collector in API processes. The collector has bounded browser page loads and graceful stop handling. Existing MongoDB data remains compatible; new timestamps include UTC offsets. Database setup/migration is a separate deployment task.

Local fixture: `ENVIRONMENT=development FIXTURE_MODE=true SCHEDULE_ENABLED=false`. The only fixture is visibly marked `[데모]`. Production rejects fixture mode. Never place API keys in images, Git, or documentation.

The integrated development Compose environment lives in the sibling nudger-server repository. The branch pipeline tests/builds only; deployment is a separate explicit action.

## Verification

Python 3.13: `pip install -r requirements-dev.txt && python -m pytest tests -q`.
Web (Node 22.12+): `cd frontend && npm ci && npm test && npm run build && npm audit`.
Vite serves local web development on port 5173 and proxies `/api` to port 8001.
Docker uses the same lock files and runs the API/collector as a non-root user.
No API key, real MongoDB connection, or Gemini call is needed by the tests.

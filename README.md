# Anew — Nudger sub app

Anew collects and summarizes news with two perspectives. Nudger Core owns users, subscriptions, delivery policy, and FCM; Anew never receives device tokens.

## Contract

`POST /api/nudger/v1/evaluate`, `Authorization: Bearer <NUDGER_SERVICE_TOKEN>` (32+ characters).

Request: `{"request_id":"job-uuid","evaluated_at":<Unix seconds>,"settings":{"schema_version":1,"keywords":["AI"],"max_items":3}}`.

Response: `status: no_content` when no fresh matching news, otherwise `notification` with stable `source_event_id`, title, body, expires_at, and `content.summary_items`. Database failures return 503. Invalid settings return 422. Each summary expires after 24 hours. Missing keyword matches never produce synthetic news. Nudger polls this endpoint; polling does not invoke Gemini.

## Run

Copy `.env.example` to `.env`, set MongoDB URI, service token, and Google API key. Run `pip install -r app/requirements.txt` and `cd app && uvicorn main:app --port 8001`. Existing React `/api/data` remains supported; static files are optional for a backend-only checkout.

`SCHEDULE_ENABLED=true` runs the existing collector in one Anew process. Do not use multiple API workers with the embedded collector; separate collector deployment is recommended at scale. MongoDB retains existing summary data. Core uses its own relational database.

Local fixture: `ENVIRONMENT=development FIXTURE_MODE=true SCHEDULE_ENABLED=false`. The only fixture is visibly marked `[데모]`. Production rejects fixture mode. Never place API keys in images, Git, or documentation.

The integrated development Compose environment lives in the sibling nudger-server repository. The branch pipeline tests/builds only; deployment is a separate explicit action.

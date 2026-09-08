# Anew — Nudger sub app

Anew collects and summarizes news with two perspectives. Nudger Core owns users, subscriptions, delivery policy, and FCM; Anew never receives device tokens.

## Contract

Collection remains limited to 매일경제·한국경제·서울경제·머니투데이·이데일리·비즈워치. `app/categories.py` defines 정치, 경제, 사회, 생활/문화, 엔터, 스포츠, IT/과학, 세계. The summary model requires exactly one valid category per topic. Categories without collected content do not produce a publication; balanced coverage of all eight categories is not guaranteed by the six financial outlets.

The standalone collector registers its manifest at Core `PUT /api/internal/sub-apps/anew/manifest` and sends `POST /api/internal/sub-apps/anew/events`, using `NUDGER_CORE_URL` and the shared service credential `NUDGER_SERVICE_TOKEN`. The old evaluate/keyword polling API is retired. Anew receives no user IDs, preferences or FCM tokens.

The MongoDB summary document stores categorized items and immutable `nudger_outbox.events` in one insert. The publisher retries pending events until their 24-hour expiry, using the same event IDs and payloads after restart. Core deduplicates replay. Each new summary document is a new publication. Old unclassified documents remain readable by the web UI but are not backfilled into notifications.

Authenticated `GET /api/nudger/v1/manifest` exposes the category metadata. Development fixture-only `POST /api/nudger/v1/demo-publish` explicitly sends one society demo publication; repeated calls in the same API process reuse the exact payload. It is unavailable in production.

## Run

Copy `.env.example` to `.env`, set MongoDB URI, Core URL (`NUDGER_CORE_URL`), service token, and Google API key. Run `pip install -r app/requirements.lock` and `cd app && uvicorn main:app --port 8001`. Existing React `/api/data` remains supported; static files are optional for a backend-only checkout.

Run one separate collector with `cd app && python -m collector`. Production rejects an embedded collector in API processes. The collector has bounded browser page loads and graceful stop handling. Existing MongoDB data remains compatible; new timestamps include UTC offsets. Database setup/migration is a separate deployment task.

Local fixture: `ENVIRONMENT=development FIXTURE_MODE=true SCHEDULE_ENABLED=false`. The only fixture is visibly marked `[데모]`. Production rejects fixture mode. Never place API keys in images, Git, or documentation.

The integrated development Compose environment lives in the sibling nudger-server repository. The branch pipeline tests/builds only; deployment is a separate explicit action.

## Verification

Python 3.13: `pip install -r requirements-dev.txt && python -m pytest tests -q`.
Web (Node 22.12+): `cd frontend && npm ci && npm test && npm run build && npm audit`.
Vite serves local web development on port 5173 and proxies `/api` to port 8001.
Docker uses the same lock files and runs the API/collector as a non-root user.
No API key, real MongoDB connection, or Gemini call is needed by the tests.

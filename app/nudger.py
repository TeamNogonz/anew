"""Anew publishes categorized events; there is no user-triggered evaluate API."""

import hashlib
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse
from fastapi import APIRouter, Header, HTTPException
from categories import LABELS, manifest
from config import settings
from database import mongodb

router = APIRouter(prefix="/api/nudger/v1", tags=["nudger"])


def build_events(document):
    """Build once at persistence time. Outbox retries reuse these exact payloads."""
    stamp = datetime.fromisoformat(document["created_at"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Publication time must include timezone")
    occurred = int(stamp.timestamp())
    groups = {}
    for item in document.get("summary_items", []):
        category = item.get("category")
        if category not in LABELS:
            raise ValueError("Anew category is required")
        references = item.get("reference_url", [])
        if not references or any(
            urlparse(url).scheme not in ("https", "http") or not urlparse(url).hostname
            for url in references
        ):
            raise ValueError("News sources must be HTTP(S) URLs")
        groups.setdefault(category, []).append(item)
    events = []
    for category, items in groups.items():
        event_id = hashlib.sha256(f"{document['_id']}:{category}".encode()).hexdigest()
        events.append(
            {
                "source_event_id": event_id,
                "category": category,
                "occurred_at": occurred,
                "expires_at": occurred + 86400,
                "title": f"Anew · {LABELS[category]} 뉴스 {len(items)}개",
                "body": " · ".join(item["title"] for item in items)[:500],
                "content": {
                    "summary_items": items,
                    "created_at": document["created_at"],
                },
            }
        )
    return events


def fixture_document():
    return {
        "_id": "local-demo-publication",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary_items": [
            {
                "category": "society",
                "title": "[데모] 도시 공원의 새로운 변화",
                "first_perspective": {
                    "title": "기대하는 점",
                    "icon": "🌱",
                    "perspectives": ["주민들이 쉴 수 있는 공간이 늘어납니다."],
                },
                "second_perspective": {
                    "title": "살펴볼 점",
                    "icon": "🔎",
                    "perspectives": ["유지 비용과 접근성을 함께 살펴야 합니다."],
                },
                "reference_url": ["https://example.com/nudger-demo"],
            }
        ],
    }


def load_latest():
    return (
        fixture_document()
        if settings.fixture_mode
        else mongodb.get_recent_summary_item()
    )


def authorized(authorization):
    if not settings.nudger_service_token or not secrets.compare_digest(
        authorization, "Bearer " + settings.nudger_service_token
    ):
        raise HTTPException(401, "Invalid service credentials")


@router.get("/manifest")
def get_manifest(authorization: str = Header(default="")):
    authorized(authorization)
    return manifest()


# Explicit fixture publication for local end-to-end tests; never enabled in production.
_fixture_events = None


@router.post("/demo-publish")
def demo_publish(authorization: str = Header(default="")):
    if not settings.fixture_mode or settings.environment == "production":
        raise HTTPException(404)
    authorized(authorization)
    from publisher import publish_events

    global _fixture_events
    if _fixture_events is None:
        _fixture_events = build_events(fixture_document())
    try:
        return {"results": publish_events(_fixture_events)}
    except Exception:
        raise HTTPException(503, "Nudger publication failed; retry the same event")

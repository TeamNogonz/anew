import copy
import time
from datetime import datetime, timezone
from unittest.mock import Mock
import httpx
import pytest
from fastapi.testclient import TestClient
from main import app
from nudger import build_events
from categories import CATEGORIES, manifest
from publisher import publish_events, flush_outbox
from config import settings
from database import mongodb, MongoDB
from summary.models import NewsSummaryItem


def document():
    return {
        "_id": "publication-1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary_items": [
            {
                "category": "society",
                "title": "도시 공원 변화",
                "first_perspective": {
                    "title": "기대",
                    "icon": "🌱",
                    "perspectives": ["휴식 공간 증가"],
                },
                "second_perspective": {
                    "title": "검토",
                    "icon": "🔎",
                    "perspectives": ["비용 검토"],
                },
                "reference_url": ["https://source.example/story"],
            }
        ],
    }


def test_eight_categories_and_retired_evaluate():
    assert [c["label"] for c in CATEGORIES] == [
        "정치",
        "경제",
        "사회",
        "생활/문화",
        "엔터",
        "스포츠",
        "IT/과학",
        "세계",
    ]
    with TestClient(app) as client:
        assert client.get("/api/nudger/v1/manifest").status_code == 401
        r = client.get(
            "/api/nudger/v1/manifest", headers={"Authorization": "Bearer " + "s" * 32}
        )
        assert r.json() == manifest()
        assert client.post("/api/nudger/v1/evaluate", json={}).status_code in (404, 405)


def test_exactly_one_valid_category_and_grouped_events():
    doc = document()
    another = copy.deepcopy(doc["summary_items"][0])
    another["category"] = "economy"
    doc["summary_items"].append(another)
    events = build_events(doc)
    assert len(events) == 2 and {e["category"] for e in events} == {
        "society",
        "economy",
    }
    assert build_events(doc) == events
    assert events[0]["source_event_id"] != events[1]["source_event_id"]
    assert len(events[0]["content"]["summary_items"]) == 1
    for value in ("unknown", ["society", "economy"], None):
        with pytest.raises(ValueError):
            NewsSummaryItem.model_validate({**another, "category": value})


def test_untrusted_sources_rejected():
    doc = document()
    doc["summary_items"][0]["reference_url"] = ["javascript:alert(1)"]
    with pytest.raises(ValueError):
        build_events(doc)


def test_publisher_sends_immutable_events_and_manifest(monkeypatch):
    monkeypatch.setattr(settings, "nudger_core_url", "http://core:8000")
    seen = []
    events = build_events(document())

    def handler(request):
        seen.append(request)
        assert request.headers["authorization"] == "Bearer " + "s" * 32
        return httpx.Response(200, json={"status": "accepted"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        publish_events(events, client)
        publish_events(events, client)
    assert [r.method for r in seen] == ["PUT", "POST", "PUT", "POST"]
    assert seen[1].content == seen[3].content


def test_summary_and_outbox_are_saved_atomically():
    db = MongoDB()
    db.collection = Mock()
    db.collection.insert_one.return_value.inserted_id = "saved"
    assert db.insert_summary_items(document()["summary_items"]) == "saved"
    record = db.collection.insert_one.call_args.args[0]
    assert record["nudger_outbox"]["status"] == "pending"
    assert record["nudger_outbox"]["events"] == build_events(record)
    assert record["summary_items"] == document()["summary_items"]


def test_failed_publication_retries_same_payload_after_restart(monkeypatch):
    import publisher

    monkeypatch.setattr(settings, "nudger_core_url", "http://core:8000")
    doc = document()
    doc["nudger_outbox"] = {
        "status": "pending",
        "attempts": 0,
        "retry_at": 0,
        "events": build_events(doc),
        "expires_at": int(time.time()) + 3600,
    }
    collection = Mock()
    collection.find.return_value.sort.return_value.limit.return_value = [doc]
    monkeypatch.setattr(mongodb, "collection", collection)
    calls = []

    def fail(events, **kwargs):
        calls.append(copy.deepcopy(events))
        raise TimeoutError()

    monkeypatch.setattr(publisher, "publish_events", fail)
    flush_outbox()
    state = collection.update_one.call_args.args[1]["$set"]
    assert state["nudger_outbox.attempts"] == 1 and "nudger_outbox.status" not in state
    monkeypatch.setattr(
        publisher,
        "publish_events",
        lambda events, **kwargs: calls.append(copy.deepcopy(events)),
    )
    flush_outbox()
    assert calls[0] == calls[1]
    assert (
        collection.update_one.call_args.args[1]["$set"]["nudger_outbox.status"]
        == "sent"
    )

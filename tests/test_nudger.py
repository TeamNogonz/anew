import os
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("GOOGLE_API_KEY", "test-only")
os.environ.setdefault("NUDGER_SERVICE_TOKEN", "s" * 32)
os.environ.setdefault("FIXTURE_MODE", "true")
os.environ.setdefault("ENVIRONMENT", "development")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from fastapi.testclient import TestClient

from main import app
from nudger import AnewSettings, build_result


def document(title="AI 산업 변화"):
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary_items": [
            {
                "title": title,
                "first_perspective": {
                    "title": "기대",
                    "icon": "🌱",
                    "perspectives": ["생산성을 높일 수 있습니다."],
                },
                "second_perspective": {
                    "title": "우려",
                    "icon": "🔎",
                    "perspectives": ["검증이 필요합니다."],
                },
                "reference_url": ["https://example.com/article"],
            }
        ],
    }


def test_contract_auth_and_fixture():
    with TestClient(app) as client:
        body = {
            "request_id": "job-1",
            "evaluated_at": int(time.time()),
            "settings": {"schema_version": 1, "keywords": [], "max_items": 3},
        }
        assert client.post("/api/nudger/v1/evaluate", json=body).status_code == 401
        response = client.post(
            "/api/nudger/v1/evaluate",
            headers={"Authorization": "Bearer " + "s" * 32},
            json=body,
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "notification"
        assert response.json()["title"].startswith("Anew")


def test_stable_event_and_keyword_filter():
    now = int(time.time())
    settings = AnewSettings(keywords=["AI"], max_items=1)
    first = build_result(document(), settings, now)
    second = build_result(document(), settings, now)
    assert first["source_event_id"] == second["source_event_id"]
    assert build_result(document("스포츠 소식"), settings, now) == {
        "status": "no_content"
    }


def test_expired_or_untrusted_sources_are_not_returned():
    old = document()
    old["created_at"] = "2020-01-01T00:00:00+00:00"
    assert build_result(old, AnewSettings(), int(time.time())) == {
        "status": "no_content"
    }

    invalid = document()
    invalid["summary_items"][0]["reference_url"] = ["javascript:alert(1)"]
    assert build_result(invalid, AnewSettings(), int(time.time())) == {
        "status": "no_content"
    }

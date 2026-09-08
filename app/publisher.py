"""Durable Mongo outbox -> authenticated Nudger publication, bounded retry."""

import logging
import time
from urllib.parse import urlparse
import httpx
from categories import manifest
from config import settings

logger = logging.getLogger(__name__)


def core_url():
    uri = urlparse(settings.nudger_core_url)
    if (
        uri.scheme not in ("http", "https")
        or not uri.hostname
        or uri.username
        or uri.password
    ):
        raise ValueError("NUDGER_CORE_URL must be a configured HTTP(S) service URL")
    if len(settings.nudger_service_token) < 32:
        raise ValueError("NUDGER_SERVICE_TOKEN must contain at least 32 characters")
    return settings.nudger_core_url.rstrip("/")


def publish_events(events, client=None, stop=None):
    if client is None:
        with httpx.Client(timeout=15) as http:
            return publish_events(events, http, stop)
    url = core_url() + "/api/internal/sub-apps/anew"
    headers = {"Authorization": "Bearer " + settings.nudger_service_token}
    # Only the configured subapp credential can update its own manifest.
    response = client.put(url + "/manifest", headers=headers, json=manifest())
    response.raise_for_status()
    results = []
    for event in events:
        if stop is not None and stop.is_set():
            raise InterruptedError("Publisher stopping")
        response = client.post(url + "/events", headers=headers, json=event)
        response.raise_for_status()
        results.append(response.json())
    return results


def flush_outbox(stop=None):
    from database import mongodb

    if not settings.nudger_core_url:
        return
    collection = mongodb.get_collection()
    now = int(time.time())
    collection.update_many(
        {"nudger_outbox.status": "pending", "nudger_outbox.expires_at": {"$lte": now}},
        {"$set": {"nudger_outbox.status": "expired"}},
    )
    for document in (
        collection.find(
            {"nudger_outbox.status": "pending", "nudger_outbox.retry_at": {"$lte": now}}
        )
        .sort("_id", 1)
        .limit(10)
    ):
        if stop is not None and stop.is_set():
            break
        state = document["nudger_outbox"]
        try:
            publish_events(state["events"], stop=stop)
            collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"nudger_outbox.status": "sent", "nudger_outbox.error": ""}},
            )
        except Exception as error:
            attempt = state.get("attempts", 0) + 1
            # Retry after restarts. All payloads/IDs remain unchanged.
            collection.update_one(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "nudger_outbox.attempts": attempt,
                        "nudger_outbox.retry_at": int(time.time())
                        + min(15 * 2 ** min(attempt, 6), 900),
                        "nudger_outbox.error": type(error).__name__,
                    }
                },
            )
            logger.warning(
                "publication_failed id=%s type=%s",
                document["_id"],
                type(error).__name__,
            )

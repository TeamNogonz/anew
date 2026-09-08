"""Versioned, authenticated content-only contract for Nudger Core."""
import hashlib
import json
import secrets
import time
from datetime import datetime
from typing import Literal
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from config import settings
from database import mongodb

router = APIRouter(prefix='/api/nudger/v1', tags=['nudger'])


class AnewSettings(BaseModel):
    model_config = ConfigDict(extra='forbid')
    schema_version: Literal[1] = 1
    keywords: list[str] = Field(default_factory=list, max_length=10)
    max_items: int = Field(default=3, ge=1, le=5)

    @field_validator('keywords')
    @classmethod
    def valid_keywords(cls, values):
        if any(not v.strip() or len(v) > 50 for v in values):
            raise ValueError('Keywords must contain 1–50 characters')
        return [v.strip() for v in values]


class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: str = Field(min_length=1, max_length=100)
    evaluated_at: int = Field(gt=0)
    settings: AnewSettings


def build_result(document, preferences, now):
    if not document:
        return {'status': 'no_content'}
    data = document.get('data', document)
    created = data.get('created_at') or document.get('created_at')
    try:
        stamp = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=ZoneInfo('Asia/Seoul'))
        expires = int(stamp.timestamp()) + 86400
    except (TypeError, ValueError):
        return {'status': 'no_content'}
    if expires <= now or stamp.timestamp() > now + 300:
        return {'status': 'no_content'}
    items = []
    for raw in data.get('summary_items', []):
        if not isinstance(raw, dict) or not raw.get('title'):
            continue
        serialized = json.dumps(raw, ensure_ascii=False).casefold()
        if preferences.keywords and not any(word.casefold() in serialized for word in preferences.keywords):
            continue
        references = [url for url in raw.get('reference_url', []) if isinstance(url, str) and urlparse(url).scheme in ('https', 'http') and urlparse(url).hostname]
        if not references:
            continue
        item = {'title': str(raw['title'])[:200], 'reference_url': references[:10]}
        for key in ('first_perspective', 'second_perspective'):
            perspective = raw.get(key) or {}
            item[key] = {'title': str(perspective.get('title', '관점'))[:100], 'icon': str(perspective.get('icon', ''))[:10], 'perspectives': [str(p)[:1000] for p in perspective.get('perspectives', [])[:5]]}
        items.append(item)
        if len(items) == preferences.max_items:
            break
    if not items:
        return {'status': 'no_content'}
    # Stable across reruns, retries, and storage IDs for the same selected stories.
    event_id = hashlib.sha256(json.dumps([{'title': item['title'], 'urls': sorted(item['reference_url'])} for item in items], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {'status': 'notification', 'source_event_id': event_id, 'title': f'Anew · 오늘의 뉴스 {len(items)}개', 'body': ' · '.join(item['title'] for item in items)[:200], 'expires_at': expires, 'content': {'summary_items': items, 'created_at': created}}


def load_latest():
    if settings.fixture_mode:
        # Explicit local demonstration; never generated or passed off as real news.
        return {'created_at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(), 'summary_items': [{'title': '[데모] 도시 공원의 새로운 변화', 'first_perspective': {'title': '기대하는 점', 'icon': '🌱', 'perspectives': ['주민들이 쉴 수 있는 공간이 늘어납니다.']}, 'second_perspective': {'title': '살펴볼 점', 'icon': '🔎', 'perspectives': ['유지 비용과 접근성을 함께 살펴야 합니다.']}, 'reference_url': ['https://example.com/nudger-demo']} ]}
    return mongodb.get_recent_summary_item()


@router.post('/evaluate')
def evaluate(body: EvaluateRequest, authorization: str = Header(default='')):
    if not settings.nudger_service_token or not secrets.compare_digest(authorization, 'Bearer ' + settings.nudger_service_token):
        raise HTTPException(401, 'Invalid service credentials')
    now = int(time.time())
    if abs(now - body.evaluated_at) > 300:
        raise HTTPException(422, 'Evaluation timestamp is stale')
    try:
        return build_result(load_latest(), body.settings, now)
    except Exception:
        # Empty news is a valid result; database failure is retryable, never no_content.
        raise HTTPException(503, 'News storage temporarily unavailable')

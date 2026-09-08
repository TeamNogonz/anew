"""Anew owns these choices; Nudger and Android consume the manifest."""

from typing import Literal

Category = Literal[
    "politics",
    "economy",
    "society",
    "life_culture",
    "entertainment",
    "sports",
    "it_science",
    "world",
]
CATEGORIES = [
    {"id": "politics", "label": "정치"},
    {"id": "economy", "label": "경제"},
    {"id": "society", "label": "사회"},
    {"id": "life_culture", "label": "생활/문화"},
    {"id": "entertainment", "label": "엔터"},
    {"id": "sports", "label": "스포츠"},
    {"id": "it_science", "label": "IT/과학"},
    {"id": "world", "label": "세계"},
]
LABELS = {item["id"]: item["label"] for item in CATEGORIES}


def manifest():
    return {
        "name": "Anew",
        "description": "선택한 카테고리의 뉴스를 두 관점으로 살펴보세요. Anew가 새 소식을 발행하면 알려드려요.",
        "category": "뉴스 · 다양한 관점",
        "categories": CATEGORIES,
    }

import json
from types import SimpleNamespace
import pytest
from summary.models import NewsSummaryRequest
from summary.services import NewsSummaryService


def service(url="https://source.example/article", sentence="검증된 요약"):
    instance = NewsSummaryService.__new__(NewsSummaryService)
    document = {
        "summary": [
            {
                "title": "뉴스",
                "category": "society",
                "reference_url": [url],
                "first_perspective": {
                    "title": "관점 1",
                    "icon": "",
                    "perspectives": [sentence],
                },
                "second_perspective": {
                    "title": "관점 2",
                    "icon": "",
                    "perspectives": ["다른 관점"],
                },
            }
        ]
    }
    instance.client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_: SimpleNamespace(text=json.dumps(document))
        )
    )
    return instance


def test_model_cannot_invent_sources():
    request = NewsSummaryRequest(news_list=[{"url": "https://source.example/article"}])
    with pytest.raises(ValueError, match="unsupported source"):
        service(url="https://invented.example/").summarize_news(request)
    assert service().summarize_news(request).summary[0].title == "뉴스"


def test_model_output_length_is_enforced():
    with pytest.raises(ValueError, match="length limit"):
        service(sentence="x" * 201).summarize_news(
            NewsSummaryRequest(news_list=[{"url": "https://source.example/article"}])
        )

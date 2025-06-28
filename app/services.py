import os
import json
from google import genai
from google.genai import types
from typing import Optional
from config import settings
from models import NewsSummaryRequest, NewsSummaryResponse, NewsSummaryItem

class NewsSummaryService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # Google Gemini API initialize
        self.client = genai.Client(api_key=settings.google_api_key)
        self.prompt_template = self._load_prompt_template("prompts/news_summary_prompt.txt")

    def _load_prompt_template(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"프롬프트 템플릿 파일을 찾을 수 없습니다: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_prompt(self, news_list: list[dict], max_length: int, summary_news_count: int) -> str:
        news_json = json.dumps(news_list, ensure_ascii=False, indent=2)
        prompt = self.prompt_template.replace("{max_length}", str(max_length))
        prompt = prompt.replace("{summary_news_count}", str(summary_news_count))
        prompt = prompt.replace("{news_json}", news_json)
        return prompt
    
    def summarize_news(self, request: NewsSummaryRequest) -> NewsSummaryResponse:
        try:
            prompt = self._get_prompt(request.news_list, request.max_length, settings.summary_news_count)

            response = self.client.models.generate_content(
                model=settings.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=settings.max_tokens,
                    temperature=settings.temperature
                ),
            )
            
            summary_text = response.text.strip()
            
            try:
                summary_data = json.loads(summary_text)
                summary_items = [NewsSummaryItem(**item) for item in summary_data]
            except json.JSONDecodeError as e:
                raise Exception(f"AI 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")
            except Exception as e:
                raise Exception(f"응답 데이터 구조가 올바르지 않습니다: {str(e)}")
            
            return NewsSummaryResponse(summary=summary_items)
            
        except Exception as e:
            raise Exception(f"요약 처리 중 오류 발생: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """API 키 유효성 검증"""
        return bool(settings.google_api_key and len(settings.google_api_key) > 0) 
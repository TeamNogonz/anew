import os
import json
import re
from google import genai
from google.genai import types
from typing import Optional
from config import settings
from logger import get_logger
from summary.models import NewsSummaryRequest, NewsSummaryResponse, NewsSummaryItem

logger = get_logger()

class NewsSummaryService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # Google Gemini API initialize
        self.client = genai.Client(api_key=settings.google_api_key)
        self.prompt_template = self._load_prompt_template("summary/prompts/news_summary_prompt.txt")

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
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """AI 응답에서 JSON 마커를 제거하고 순수한 JSON만 추출"""
        # JSON 마커 패턴들
        patterns = [
            r'```json\s*(.*?)\s*```',  # ```json ... ```
            r'```\s*(.*?)\s*```',      # ``` ... ```
            r'`(.*?)`',                # ` ... `
        ]
        
        # 각 패턴으로 JSON 추출 시도
        for pattern in patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # 마커가 없으면 전체 텍스트 반환 (이미 순수 JSON일 가능성)
        return response_text.strip()
    
    def summarize_news(self, request: NewsSummaryRequest) -> NewsSummaryResponse:
        try:
            prompt = self._get_prompt(request.news_list, request.max_length or 200, settings.summary_news_count)

            response = self.client.models.generate_content(
                model=settings.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=settings.max_tokens,
                    temperature=settings.temperature
                ),
            )
            
            summary_text = response.text.strip() if response.text else ""

            logger.info(f"AI 요약 응답: {summary_text[:200]}...")  # 로그에 응답 일부 기록
            
            try:
                # JSON 마커 제거 및 순수 JSON 추출
                cleaned_text = self._extract_json_from_response(summary_text)
                summary_data = json.loads(cleaned_text)
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
from google import genai
from google.genai import types
from typing import Optional
from config import settings
from models import NewsSummaryRequest, NewsSummaryResponse

class NewsSummaryService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # Google Gemini API 설정
        self.client = genai.Client(api_key=settings.google_api_key)

        # genai.configure(api_key=settings.google_api_key)
        # self.model = genai.GenerativeModel(settings.model_name)
    
    def _get_prompt(self, content: str, max_length: int) -> str:
            return f"""
다음 뉴스 내용을 {max_length}자 이내로 요약해주세요. 
요약은 핵심 내용만 포함하고, 객관적이고 명확하게 작성해주세요.

뉴스 내용:
{content}

요약:
"""
    
    def summarize_news(self, request: NewsSummaryRequest) -> NewsSummaryResponse:
        try:
            prompt = self._get_prompt(request.content, request.max_length)

            response = self.client.models.generate_content(
                model=settings.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=settings.max_tokens,
                    temperature=settings.temperature
                ),
            )
            
            summary = response.text.strip()
            
            original_length = len(request.content)
            summary_length = len(summary)
            compression_ratio = round((summary_length / original_length) * 100, 2)
            
            return NewsSummaryResponse(
                original_length=original_length,
                summary=summary,
                summary_length=summary_length,
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            raise Exception(f"요약 처리 중 오류 발생: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """API 키 유효성 검증"""
        return bool(settings.google_api_key and len(settings.google_api_key) > 0) 
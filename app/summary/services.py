import os
import json
import re
import google.generativeai as genai
import http.client as httplib
from config import settings
from logger import get_logger
from summary.models import NewsSummaryRequest, NewsSummaryResponse, NewsSummaryItem

logger = get_logger()

class NewsSummaryService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # Google Gemini API initialize
        genai.configure(api_key=settings.google_api_key)
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
    
    def _generate_with_fallback(self, prompt: str) -> str:
        """메인 모델과 예비 모델들을 사용하여 재시도"""
        models_to_try = [settings.model_name] + settings.fallback_models
        
        for model_name in models_to_try:
            try:
                logger.info(f"모델 {model_name}로 요청 시도")
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=settings.max_tokens,
                        temperature=settings.temperature
                    )
                )
                
                if response.text:
                    logger.info(f"모델 {model_name}로 성공적으로 응답 받음")
                    return response.text.strip()
                
            except Exception as e:
                if hasattr(e, 'response') and e.response.status_code == httplib.SERVICE_UNAVAILABLE:
                    logger.warning(f"모델 {model_name}에서 서비스 과부하 에러. 상태 코드: {e.response.status_code}. 다음 모델로 시도합니다...")
                    continue
                else:
                    logger.error(f"모델 {model_name}에서 예상치 못한 에러 발생: {e}")
                    raise e
        
        logger.error("모든 모델이 응답 생성에 실패했습니다.")
        raise Exception("모든 모델이 응답 생성에 실패했습니다.")
    
    def summarize_news(self, request: NewsSummaryRequest) -> NewsSummaryResponse:
        try:
            prompt = self._get_prompt(request.news_list, request.max_length or 200, settings.summary_news_count)

            summary_text = self._generate_with_fallback(prompt)

            logger.info(f"AI 요약 응답: {summary_text[:200]}...")  # 로그에 응답 일부 기록
            
            try:
                # JSON 마커 제거 및 순수 JSON 추출
                cleaned_text = self._extract_json_from_response(summary_text)
                summary_data = json.loads(cleaned_text)
                summary_items = [NewsSummaryItem(**item) for item in summary_data]
            except json.JSONDecodeError as e:
                # JSON 파싱 실패 시 원본 응답을 파일로 저장
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"failed_response_{timestamp}.txt"
                
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(summary_text)
                    logger.error(f"JSON 파싱 실패. 원본 응답을 {filename}에 저장했습니다.")
                except Exception as save_error:
                    logger.error(f"파일 저장 중 오류: {save_error}")
                
                raise Exception(f"AI 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")
            except Exception as e:
                raise Exception(f"응답 데이터 구조가 올바르지 않습니다: {str(e)}")
            
            return NewsSummaryResponse(summary=summary_items)
            
        except Exception as e:
            raise Exception(f"요약 처리 중 오류 발생: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """API 키 유효성 검증"""
        return bool(settings.google_api_key and len(settings.google_api_key) > 0)

if __name__ == "__main__":
    # 테스트용 더미 뉴스 데이터
    dummy_news = [
        {
            "press": "테스트뉴스",
            "url": "https://example.com/news1",
            "title": "AI 기술 발전으로 새로운 가능성 열려",
            "content": "최근 AI 기술의 급속한 발전으로 다양한 분야에서 혁신이 일어나고 있습니다. 특히 자연어 처리 기술의 향상으로 더욱 정확한 텍스트 분석이 가능해졌습니다."
        },
        {
            "press": "테스트뉴스",
            "url": "https://example.com/news2", 
            "title": "머신러닝 모델 성능 향상",
            "content": "새로운 머신러닝 알고리즘의 개발로 모델 성능이 크게 향상되었습니다. 이는 더 정확한 예측과 분석을 가능하게 합니다."
        },
        {
            "press": "테스트뉴스",
            "url": "https://example.com/news3",
            "title": "데이터 사이언스 분야 확장",
            "content": "데이터 사이언스 분야가 다양한 산업에 적용되면서 새로운 가치를 창출하고 있습니다. 빅데이터 분석을 통한 인사이트 도출이 핵심입니다."
        }
    ]
    
    try:
        # 서비스 인스턴스 생성
        service = NewsSummaryService()
        
        # API 키 유효성 검증
        if service.validate_api_key():
            print("✅ API 키 유효성 검증 성공")
            
            # 뉴스 요약 요청 생성
            from .models import NewsSummaryRequest
            request = NewsSummaryRequest(
                news_list=dummy_news,
                max_length=150
            )
            
            print("🔄 뉴스 요약 시작...")
            print(f"🔄 처리할 뉴스: {len(dummy_news)}개")
            
            # 요약 실행
            response = service.summarize_news(request)
            
            print("✅ 요약 완료!")
            print(f"📊 생성된 요약: {len(response.summary)}개")
            
            # 결과 출력
            for i, item in enumerate(response.summary, 1):
                print(f"\n--- 요약 {i} ---")
                print(f"제목: {item.title}")
                print(f"첫 번째 관점: {item.first_perspective.title}")
                print(f"두 번째 관점: {item.second_perspective.title}")
                print(f"참조 URL: {len(item.reference_url)}개")
                
        else:
            print("❌ API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc() 
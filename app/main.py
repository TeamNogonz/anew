from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from summary.models import NewsSummaryRequest, NewsSummaryResponse
from summary.services import NewsSummaryService
from database import mongodb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

news_service = None

def get_news_service() -> NewsSummaryService:
    global news_service
    if news_service is None:
        try:
            news_service = NewsSummaryService()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return news_service

@app.on_event("startup")
async def startup_event():
    try:
        # MongoDB 연결
        # mongodb.connect()
        # logger.info("MongoDB 연결 완료")
        
        # 뉴스 서비스 초기화
        service = get_news_service()
        if not service.validate_api_key():
            logger.warning("Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
        logger.info("server started..")
    except Exception as e:
        logger.error(f"서비스 초기화 중 오류: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # mongodb.disconnect()
    logger.info("server shutdown..")

@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/summarize", response_model=NewsSummaryResponse)
def summarize_news(
    request: NewsSummaryRequest,
    service: NewsSummaryService = Depends(get_news_service)
):
    try:
        result = service.summarize_news(request)
        return result
    except Exception as e:
        logger.exception("뉴스 요약 중 예외 발생")
        raise HTTPException(status_code=500, detail=str(e))
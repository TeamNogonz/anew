from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import settings
from summary.models import NewsSummaryRequest, NewsSummaryResponse
from summary.services import NewsSummaryService
from database import mongodb
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"정적 파일 디렉토리 마운트: {static_dir}")
else:
    logger.warning(f"정적 파일 디렉토리를 찾을 수 없습니다: {static_dir}")

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

@app.get("/")
async def serve_react_app():
    """리액트 앱의 index.html을 제공"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "React app not found. Please build and place in static directory."}

@app.get("/{full_path:path}")
async def serve_react_routes(full_path: str):
    """리액트 라우팅을 위한 fallback - 모든 경로를 index.html로 리다이렉트"""
    # API 경로는 제외
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="React app not found")

@app.post("/api/summarize", response_model=NewsSummaryResponse)
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
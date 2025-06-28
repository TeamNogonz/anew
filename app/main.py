from fastapi import FastAPI, HTTPException, Depends, Request
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

build_dir = os.path.join(os.path.dirname(__file__), "static")
static_assets_dir = os.path.join(build_dir, "static")

app.mount("/static", StaticFiles(directory=static_assets_dir), name="static")

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
        mongodb.connect()
        
        # 뉴스 서비스 초기화
        service = get_news_service()
        if not service.validate_api_key():
            logger.warning("Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
        logger.info("server started..")
    except Exception as e:
        logger.error(f"서비스 초기화 중 오류: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    mongodb.disconnect()
    logger.info("server shutdown..")

@app.get("/api/ping")
def ping():
    return {"message": "pong"}

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = os.path.join(build_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "React app not found. Please build and place in static directory."}
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from summary.services import NewsSummaryService
from database import mongodb
from logger import get_logger
from config import settings
import os
import threading

# 로거 설정 (uvicorn 로거도 포함)
logger = get_logger()

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

def init_schedule():
    """백그라운드에서 스케줄러 실행"""
    try:
        from scheduler import NewsScheduler
        
        logger.info(f"스케줄러 시작 - {settings.schedule_interval}시간 간격")
        scheduler = NewsScheduler()
        scheduler.start_scheduler(settings.schedule_interval)
    except Exception as e:
        logger.error(f"스케줄러 시작 중 오류: {e}")
        if 'scheduler' in locals():
            scheduler.stop_scheduler()

@app.on_event("startup")
async def startup_event():
    try:
        mongodb.connect()
        
        # 뉴스 서비스 초기화
        service = get_news_service()
        if not service.validate_api_key():
            logger.warning("Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
        
        # 스케줄러를 백그라운드 스레드로 시작
        if settings.schedule_enabled:
            scheduler_thread = threading.Thread(target=init_schedule, daemon=True)
            scheduler_thread.start()
            logger.info("스케줄러 백그라운드 스레드 시작")
        
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

@app.get("/api/data")
def get_summary():
    response = mongodb.get_recent_summary_item()
    
    if not response:
        return {"summary_items": [], "created_at": None}
    
    if 'data' in response:
        summary_items = response.get('data', {}).get('summary_items', [])
        created_at = response.get('data', {}).get('created_at')
    else:
        summary_items = response.get('summary_items', [])
        created_at = response.get('created_at')
    
    return {"summary_items": summary_items, "created_at": created_at}

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = os.path.join(build_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "React app not found. Please build and place in static directory."}
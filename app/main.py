from contextlib import asynccontextmanager
import os
import threading
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import settings
from database import mongodb
from nudger import router, load_latest
from logger import get_logger

logger = get_logger()


@asynccontextmanager
async def lifespan(app):
    if len(settings.nudger_service_token) < 32:
        raise RuntimeError('NUDGER_SERVICE_TOKEN must contain at least 32 characters')
    if settings.fixture_mode and settings.environment == 'production':
        raise RuntimeError('Fixture mode is prohibited in production')
    scheduler = None
    thread = None
    if not settings.fixture_mode:
        mongodb.connect()
        if settings.schedule_enabled:
            from scheduler import NewsScheduler
            scheduler = NewsScheduler()
            thread = threading.Thread(target=scheduler.start_scheduler, daemon=True)
            thread.start()
    try:
        yield
    finally:
        if scheduler:
            scheduler.stop_scheduler()
        if thread:
            thread.join(timeout=5)
        mongodb.disconnect()


app = FastAPI(title='Anew · Nudger Sub App', version='2.0.0', lifespan=lifespan)
app.include_router(router)
build_dir = os.path.join(os.path.dirname(__file__), 'static')
assets = os.path.join(build_dir, 'static')
if os.path.isdir(assets):
    app.mount('/static', StaticFiles(directory=assets), name='static')


@app.get('/api/ping')
def ping():
    return {'message': 'pong', 'version': '2.0.0'}


@app.get('/ready')
def ready():
    if not settings.fixture_mode:
        mongodb.client.admin.command('ping')
    return {'status': 'ready'}


@app.get('/api/data')
def get_summary():
    try:
        document = load_latest() or {}
        data = document.get('data', document)
        return {'summary_items': data.get('summary_items', []), 'created_at': data.get('created_at')}
    except Exception:
        raise HTTPException(503, 'News storage temporarily unavailable')


@app.get('/{full_path:path}')
def frontend(full_path: str):
    if full_path.startswith('api/'):
        raise HTTPException(404)
    index = os.path.join(build_dir, 'index.html')
    if os.path.isfile(index):
        return FileResponse(index)
    return {'service': 'Anew', 'docs': '/docs'}

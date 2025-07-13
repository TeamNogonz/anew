import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from config import settings

def setup_logger() -> logging.Logger:
    # 로그 디렉토리 생성
    log_dir = settings.log_dir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 공통 로거 생성
    logger = logging.getLogger("anew")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # 이미 핸들러가 설정되어 있다면 중복 방지
    if logger.handlers:
        return logger
    
    # 포맷터 설정
    formatter = logging.Formatter(settings.log_format)
    
    # 콘솔 핸들러 (기본)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (날짜별 로테이션) - 모든 로그 레벨 저장
    today = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_dir, f"{today}.log")
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when='midnight',  # 매일 자정에 로테이션
        interval=1,       # 1일 간격
        backupCount=30,   # 30일치 보관
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 모든 로그 레벨을 파일에 저장
    file_handler.setFormatter(formatter)
    
    # 로테이션 시 파일명에 날짜 추가
    file_handler.suffix = "%Y-%m-%d"
    logger.addHandler(file_handler)
    
    # uvicorn 로거들도 동일한 핸들러 사용
    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error")
    ]
    
    for uvicorn_logger in uvicorn_loggers:
        uvicorn_logger.handlers.clear()  # 기존 핸들러 제거
        uvicorn_logger.addHandler(console_handler)
        uvicorn_logger.addHandler(file_handler)
        uvicorn_logger.setLevel(logging.DEBUG)
        uvicorn_logger.propagate = False
    
    return logger

def get_logger() -> logging.Logger:
    return setup_logger() 
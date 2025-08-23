import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "500"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    summary_news_count: int = int(os.getenv("SUMMARY_NEWS_COUNT", "3"))
    
    # MongoDB 설정
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "news_summary")
    mongodb_collection: str = os.getenv("MONGODB_COLLECTION", "summaries")
    
    # 로그 설정
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "logs")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # 스케줄러 설정
    schedule_interval: int = int(os.getenv("SCHEDULE_INTERVAL", "1"))  # 시간 단위
    schedule_enabled: bool = os.getenv("SCHEDULE_ENABLED", "true").lower() == "true"

settings = Settings() 
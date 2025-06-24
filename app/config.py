import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "500"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))

settings = Settings() 
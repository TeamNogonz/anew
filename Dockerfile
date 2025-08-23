# ==============================
# 1. React 빌드 스테이지
# ==============================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 의존성 설치 (devDependencies 포함)
COPY frontend/package*.json ./
RUN npm ci

# 프론트엔드 소스 복사 및 빌드
COPY frontend/ .
RUN npm run build


# ==============================
# 2. Python + Chromium + ChromeDriver 스테이지
# ==============================
FROM python:3.10-slim

WORKDIR /app

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    ca-certificates \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libvulkan1 \
    libglib2.0-0 \
    libu2f-udev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Chromium 설치
RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치 (Chrome/Chromium v139 기준)
RUN CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_139) \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Python 의존성 설치
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 애플리케이션 복사
COPY app/ .

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-builder /app/frontend/build ./static

# 로그 디렉토리 생성 및 권한 설정
RUN mkdir -p logs && chmod 755 logs

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

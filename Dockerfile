# ==============================
# 1. React 빌드 스테이지
# ==============================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 프론트엔드 의존성 설치
COPY frontend/package*.json ./
RUN npm ci

# 프론트엔드 소스 복사 및 빌드
COPY frontend/ .
RUN npm run build

# ==============================
# 2. Python + Chromium + Selenium 스테이지
# ==============================
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치
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
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY app/ .

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-builder /app/frontend/build ./static

# 로그 디렉토리 생성 및 권한 설정
RUN mkdir -p logs && chmod 755 logs

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

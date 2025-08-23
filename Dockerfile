# 멀티스테이지 빌드: React 빌드 스테이지
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 프론트엔드 의존성 설치
COPY frontend/package*.json ./
RUN npm ci --only=production

# 프론트엔드 소스 복사 및 빌드
COPY frontend/ .
RUN npm run build

---

# Python 애플리케이션 스테이지
# Python 이미지 대신 selenium/standalone-chrome-py 이미지 사용
# 이 이미지는 Chrome, chromedriver, Python, 그리고 Selenium을 미리 포함하고 있어 편리합니다.
FROM selenium/standalone-chrome:latest

# WORKDIR 설정
WORKDIR /app

# 시스템 및 Python 의존성 설치
# `selenium/standalone-chrome` 이미지에는 Python이 이미 설치되어 있지만,
# 필요한 라이브러리가 없을 수 있으므로 pip install 과정을 추가합니다.
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 애플리케이션 복사
COPY app/ .

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-builder /app/frontend/build ./static

# 로그 디렉토리 생성 및 권한 설정
RUN mkdir -p logs && chmod 755 logs

# # 환경변수 설정
# # 기존에 selenium 이미지에 설정되어 있으므로 필요에 따라 주석 해제
# ENV PYTHONPATH=/app
# ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
# 기존 uvicorn 실행 명령어를 사용
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
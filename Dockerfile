# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# (선택) 빌드시 필요한 툴
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 의존성 먼저 설치 (레이어 캐시 최적화)
COPY requirements.txt /app/

ENV PYTHONHTTPSVERIFY=0
# SSL 인증서 검증 비활성화 (비권장)
# RUN pip install --upgrade pip
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# 소스 복사
COPY . /app

# 패키지 import 경로 보장
ENV PYTHONPATH=/app

# 비루트 유저
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 운영 기본: Gunicorn이 팩토리 함수를 직접 호출
# -> minigame:create_app('prod')
CMD ["gunicorn", "--factory", "-w", "2", "-b", "0.0.0.0:8000", "minigame:create_app"]

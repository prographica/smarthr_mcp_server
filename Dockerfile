# SmartHR MCP Server - Cloud Run 向けコンテナ
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依存だけ先に入れてレイヤキャッシュを効かせる
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY main.py ./
COPY smarthr_mcp_server/ ./smarthr_mcp_server/

# Cloud Run は $PORT を注入する (既定 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]

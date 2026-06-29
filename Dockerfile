# ECO-IA API — OVHcloud US b3-8 | Ubuntu 24.04 | Python 3.12
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl rsync openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 ecouser && chown -R ecouser:ecouser /app
USER ecouser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

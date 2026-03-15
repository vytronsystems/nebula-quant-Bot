FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# deps mínimas (curl para debug)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 1) requirements — install from PyPI (wheelhouse optional; use when present for offline)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) código
COPY . .

CMD ["python", "/app/bot/__main__.py"]

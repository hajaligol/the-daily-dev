# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies:
# - libpq5 is required at runtime by psycopg (PostgreSQL client library)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as a non-root user.
RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/healthz/').status == 200 else sys.exit(1)"

ENTRYPOINT ["./docker-entrypoint.sh"]

FROM python:3.11-slim AS base

# Never run as root inside containers
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Install dependencies first (layer caching)
COPY simulator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator package
COPY simulator/ ./simulator/

# Switch to non-root user
USER appuser

ENTRYPOINT ["python", "-m", "simulator"]
CMD ["--output", "/app/data/signal_log.parquet"]

# ---------- Builder Stage ----------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency manifests first for better layer caching
COPY pyproject.toml ./

# If you use uv.lock, copy it too
COPY uv.lock* ./

# Install dependencies from pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

# ---------- Runtime Stage ----------
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Runtime packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . /app

EXPOSE 8000

CMD ["gunicorn", "Daniel.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./

# Install dependencies directly from pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r pyproject.toml

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "Daniel.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
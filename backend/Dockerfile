FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (production only)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Collect static files (SECRET_KEY фиктивный — только для сборки статики)
RUN DJANGO_SECRET_KEY=build-only-not-for-prod \
    POSTGRES_PASSWORD=build \
    DATABASE_URL=sqlite:////tmp/build.db \
    uv run python manage.py collectstatic --noinput --settings=config.settings.prod

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]

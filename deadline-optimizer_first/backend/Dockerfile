FROM python:3.12-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies via pip
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    asyncpg \
    pydantic \
    pydantic-settings \
    python-dotenv \
    httpx \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

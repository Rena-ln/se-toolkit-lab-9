FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy nanobot files (relative to build context)
COPY config.json /app/config.json
COPY entrypoint.py /app/entrypoint.py

# Install nanobot
RUN uv tool install nanobot || pip install nanobot || true

# Expose ports
EXPOSE 18790 8765

# Run entrypoint
CMD ["python", "/app/entrypoint.py"]

# # ---------- base image ----------------------------------------------------
# FROM python:3.11-slim

# WORKDIR /

# # Install system dependencies including antiword and Tesseract
# RUN apt-get update && \
#     apt-get install -y antiword tesseract-ocr libtesseract-dev libreoffice && \
#     rm -rf /var/lib/apt/lists/*

# COPY ./requirements.txt /requirements.txt


# RUN pip install -r /requirements.txt

# RUN playwright install chromium
# RUN playwright install-deps chromium

# COPY ./app /app/
# # WORKDIR /app

# CMD ["fastapi", "run", "/app/app.py", "--port", "5000"]

# # If running behind a proxy like Nginx or Traefik add --proxy-headers
# # CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]

# ---------- base image ----------------------------------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ---------- system packages ----------------------------------------------
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        antiword tesseract-ocr libtesseract-dev libreoffice && \
    rm -rf /var/lib/apt/lists/*

# playwright and its dependencies
RUN pip install --no-cache-dir playwright && \
    playwright install-deps chromium && \
    playwright install chromium

# ---------- application user & workdir -----------------------------------
RUN adduser --disabled-password --gecos '' appuser
USER appuser
WORKDIR /app

# ---------- Python dependencies ------------------------------------------
COPY --chown=appuser:appuser requirements.txt .
RUN pip install -r requirements.txt

# ---------- application code ---------------------------------------------
COPY --chown=appuser:appuser ./app ./app

# ---------- entrypoint ----------------------------------------------------
CMD ["gunicorn", "app:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--log-level", "info"]

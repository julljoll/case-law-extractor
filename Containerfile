# ==============================================================================
# Case Law Extractor powered by sha256.us
# Containerfile for Podman / Docker
# Plataforma: Python 3.11-slim + Playwright Chromium headless
# ==============================================================================

FROM python:3.11-slim

LABEL maintainer="sha256.us"
LABEL description="Case Law Extractor - TSJ Venezuela Jurisprudence Dashboard"
LABEL version="2.0"

# --- System dependencies for Playwright Chromium ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory ---
WORKDIR /app

# --- Python dependencies (cached layer) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Install Playwright Chromium browser ---
RUN playwright install chromium --with-deps

# --- Copy application source code ---
COPY . .

# --- Persistent data directory (SQLite + Excel outputs) ---
RUN mkdir -p /app/data/Databases_SQLite /app/data/Excel_Buscador

# --- Expose Dash dashboard port ---
EXPOSE 8050

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# --- Entrypoint: run the dashboard ---
CMD ["python", "main.py", "--dashboard"]

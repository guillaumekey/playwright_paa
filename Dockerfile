FROM python:3.12-slim-bookworm

WORKDIR /app

# Dependances systeme pour Chrome + Xvfb (nodriver ne supporte pas bien headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
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
    libxrandr2 \
    xdg-utils \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Installer Google Chrome stable (requis par nodriver et undetected-chromedriver)
RUN wget -q -O /tmp/chrome.deb \
    https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Demarrage: Xvfb en arriere-plan + uvicorn
RUN chmod +x start.sh
EXPOSE 10000
CMD ["./start.sh"]

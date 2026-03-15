FROM python:3.11-slim

WORKDIR /app

# System dependency needed for discord voice playback
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Runtime writable directories
RUN mkdir -p /app/temp /app/savedplaylists

CMD ["python", "carpbot.py"]

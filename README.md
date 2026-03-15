# CarpBot

CarpBot is a discord bot that displays images of certain things. These images are divided in groups. You can add links and remove them from discord as well as some other functions

## Run with Docker

### 1) Configure environment variables

Create a .env file based on .env.example and set your real values:

- DISCORD_TOKEN
- DEV_USER (comma-separated Discord user IDs)
- LYRICS (optional, for lyrics commands)

### 2) Start with Docker Compose

Build and run in background:

docker compose up -d --build

Follow logs:

docker compose logs -f carpbot

Stop:

docker compose down

### Notes

- The image installs ffmpeg for voice playback.
- The following folders are mounted as volumes to persist data:
    - sources
    - savedplaylists
    - temp

# Whisper Transcriber

A local transcription service for video and audio files powered by **OpenAI Whisper**, with a web UI and MongoDB-backed history.

---

## 📁 Project structure

```
transcript/
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Service configuration (whisper + mongo)
├── pyproject.toml        # Python dependencies (managed by uv)
├── uv.lock               # Locked dependency versions
└── src/
    ├── app.py            # FastAPI backend
    ├── db.py             # MongoDB access layer
    └── static/
        ├── index.html    # Transcription UI
        ├── history.html  # History browser UI
        └── styles.css    # Shared styles
```

---

## 🚀 Getting started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Build the image

```bash
docker compose build
```

### 2. Start the service

```bash
docker compose up
```

### 3. Open your browser

```
http://localhost:8000
```

---

## Usage

### Web UI

**Transcribe tab** (`/`)
1. Drop a file onto the upload zone or click to browse
2. Select the language (default: English)
3. Click **Transcribe**
4. Wait for the result — on CPU, transcription takes roughly 1–3× the length of the audio

**History tab** (`/history`)
- Browse all past transcriptions
- Search by filename or content
- Sort by date or filename (ascending/descending)
- Click any entry to view the full text and timestamps


## Supported formats

| Type  | Formats                                 |
| ----- | --------------------------------------- |
| Video | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |

---

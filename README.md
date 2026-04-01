# Whisper Transcriber

A local transcription service for video and audio files powered by **OpenAI Whisper**.

---

## 📁 Project structure

```
whisper-docker/
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Service configuration
├── pyproject.toml        # Python dependencies (managed by uv)
├── uv.lock               # Locked dependency versions
├── app.py                # FastAPI backend
└── static                # Web UI
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

1. Open `http://localhost:8000`
2. Drop a file onto the upload zone or click to browse
3. Select the language (default: English)
4. Click **Transcribe**
5. Wait for the result — on CPU, transcription takes roughly 1–3× the length of the audio

### API (curl / code)

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@my_recording.mp4" \
  -F "language=en"
```

Example response:

```json
{
  "filename": "my_recording.mp4",
  "language": "en",
  "text": "Hello, this is a sample transcription...",
  "segments": [
    { "start": 0.0, "end": 2.5, "text": "Hello, this is a sample" },
    { "start": 2.5, "end": 4.1, "text": "transcription." }
  ]
}
```

### Health check

```bash
curl http://localhost:8000/health
```

---

## Supported formats

| Type  | Formats                                 |
| ----- | --------------------------------------- |
| Video | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |

---

## Changing the Whisper model

Edit the following line in `app.py`:

```python
model = whisper.load_model("small")
```

Available models (fastest to most accurate):

| Model     | Size       | CPU ~(1 min audio) | Quality                 |
| --------- | ---------- | ------------------ | ----------------------- |
| tiny      | 75 MB      | ~10s               | basic                   |
| base      | 145 MB     | ~20s               | good                    |
| **small** | **490 MB** | **~60s**           | **very good** ← current |
| medium    | 1.5 GB     | ~3 min             | great                   |
| large     | 3 GB       | ~6 min             | best                    |

---

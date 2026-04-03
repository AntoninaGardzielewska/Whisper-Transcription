import os
import shutil
import uuid

import whisper
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

from src.db import NotFoundError, SortTranscripts, TranscriptDB

app = FastAPI(title="Whisper Transcription API")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
db = TranscriptDB(client)

print("Loading Whisper model 'small'...")
model = whisper.load_model("small")
print("Model ready!")

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
    ".flac",
}


def validate_extension(filename: str) -> str:
    """Checks the file extension and returns it, or raises HTTP 400."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return ext


def save_temp_file(upload: UploadFile, ext: str) -> str:
    """Saves the uploaded file to the temporary directory, returns the path."""
    tmp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return tmp_path


def run_transcription(tmp_path: str, language: str) -> dict:
    """Runs Whisper on the given file and returns the raw result."""
    return model.transcribe(
        tmp_path,
        language=language if language != "auto" else None,
        verbose=False,
    )


def format_segments(raw_segments: list) -> list:
    """Transforms raw Whisper segments into a clean JSON format."""
    return [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        for seg in raw_segments
    ]


def delete_temp_file(path: str) -> None:
    """Deletes the temporary file if it exists."""
    if os.path.exists(path):
        os.remove(path)


# --- Endpoints ---


@app.get("/")
def root():
    return FileResponse("src/static/index.html")

@app.get("/history")
def history_page():
    return FileResponse("src/static/history.html")

# @app.get("/styles.css")
# def styles():
#     return FileResponse("static/styles.css")


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
):
    ext = validate_extension(file.filename)
    tmp_path = save_temp_file(file, ext)

    try:
        print(f"Transcribing: {file.filename} (language: {language})")
        result = run_transcription(tmp_path, language)
        segments = format_segments(result["segments"])
        db.insert_item(file.filename, language, result["text"].strip(), segments)
        print(f"Done: {file.filename} — detected language: {result['language']}")

        return JSONResponse(
            {
                "filename": file.filename,
                "language": result["language"],
                "text": result["text"].strip(),
                "segments": segments,
            }
        )
    finally:
        delete_temp_file(tmp_path)


@app.get("/history-page")
def get_history(sort_by: str = "DATE_DECREASING"):
    sort = SortTranscripts[sort_by]
    return db.get_all(sort_by=sort)


@app.get("/transcript/{id}")
def get_transcript(id: str):
    try:
        transcript = db.get_item(id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return transcript


@app.get("/health")
def health():
    return {"status": "ok", "model": "whisper-small"}

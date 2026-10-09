import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from transcription import transcribe_audio

app = FastAPI()

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg"}
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"


@app.get("/")
def read_root():
    return {"message": "AI Call Center Analyzer API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_audio(file: UploadFile = File(...)):
    filename = file.filename or ""
    file_extension = ""
    if "." in filename:
        file_extension = "." + filename.rsplit(".", 1)[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a .wav, .mp3, .m4a, or .ogg file.",
        )

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = UPLOADS_DIR / f"{uuid.uuid4()}{file_extension}"

    try:
        with temp_path.open("wb") as saved_file:
            shutil.copyfileobj(file.file, saved_file)

        try:
            transcript = transcribe_audio(str(temp_path))
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Transcription failed. Please try again with a valid audio file.",
            )

        return {
            "filename": filename,
            "transcript": transcript,
            "message": "Audio transcribed successfully",
        }
    finally:
        if temp_path.exists():
            temp_path.unlink()


import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from transcription import transcribe_audio
from analysis import analyze_transcript

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail="No speech was detected in the audio file.",
            )

        try:
            analysis = analyze_transcript(transcript)
        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Call analysis failed. Please try again later.",
            )

        return {
            "filename": filename,
            "transcript": transcript,
            "analysis": analysis,
            "message": "Audio transcribed and analyzed successfully",
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()

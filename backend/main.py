
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.analysis import analyze_transcript
from backend.conversation import process_conversation

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "https://ai-call-center-analyzer.vercel.app",
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
            conversation = process_conversation(str(temp_path))
        except Exception:
            logger.exception(
                "Conversation processing failed for '%s'", filename
            )
            raise HTTPException(
                status_code=500,
                detail="Conversation processing failed. Please try again with a valid audio file.",
            )

        if not conversation:
            raise HTTPException(
                status_code=422,
                detail="No speech was detected in the audio file.",
            )

        transcript = "\n".join(
            f"[{segment['start']:.2f}s - {segment['end']:.2f}s] "
            f"{segment['speaker']}: {segment['text']}"
            for segment in conversation
        )

        try:
            analysis = analyze_transcript(transcript)
        except Exception:
            logger.exception(
                "Call analysis failed for '%s'", filename
            )
            raise HTTPException(
                status_code=502,
                detail="Call analysis failed. Please try again later.",
            )

        # Map each speaker ID to its role identified by Gemini.
        speaker_roles = analysis.get("speaker_roles", {})

        for segment in conversation:
            segment["speaker_role"] = speaker_roles.get(
                segment["speaker"],
                "Unknown"
            )

        return {
            "filename": filename,
            "conversation": conversation,
            "transcript": transcript,
            "analysis": analysis,
            "message": "Audio transcribed and analyzed successfully",
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()

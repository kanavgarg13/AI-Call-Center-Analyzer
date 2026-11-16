
from faster_whisper import WhisperModel


def transcribe_audio_segments(audio_path: str) -> list[dict]:
    """Turn an audio file into timed transcript segments."""
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _info = model.transcribe(audio_path)

        transcript_segments = []

        for segment in segments:
            text = segment.text.strip()

            if text:
                transcript_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": text,
                })

        return transcript_segments

    except Exception as error:
        raise RuntimeError(
            f"Failed to transcribe audio at '{audio_path}': {error}"
        ) from error

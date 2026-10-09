from faster_whisper import WhisperModel


def transcribe_audio(audio_path: str) -> str:
    """Turn an audio file into a single transcript string."""
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _info = model.transcribe(audio_path)

        transcript_parts = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                transcript_parts.append(text)

        return " ".join(transcript_parts)
    except Exception as error:
        raise RuntimeError(
            f"Failed to transcribe audio at '{audio_path}': {error}"
        ) from error

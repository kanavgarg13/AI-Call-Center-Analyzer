from backend.diarization import diarize_audio
from backend.transcription_v2 import transcribe_audio_segments


def process_conversation(audio_path: str) -> list[dict]:
    """Assign a speaker to each transcription segment."""
    try:
        transcript_segments = transcribe_audio_segments(audio_path)
        speaker_segments = diarize_audio(audio_path)

        conversation = []
        for transcript in transcript_segments:
            transcript_start = transcript["start"]
            transcript_end = transcript["end"]
            best_speaker = "UNKNOWN"
            best_overlap = 0.0

            for speaker in speaker_segments:
                overlap = max(
                    0,
                    min(transcript_end, speaker["end"])
                    - max(transcript_start, speaker["start"]),
                )
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = speaker["speaker"]

            conversation.append(
                {
                    "start": transcript_start,
                    "end": transcript_end,
                    "speaker": best_speaker,
                    "text": transcript["text"],
                }
            )

        return conversation
    except Exception as error:
        raise RuntimeError(
            f"Failed to process conversation at '{audio_path}': {error}"
        ) from error

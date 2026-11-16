import os

import soundfile as sf
import torch
from pyannote.audio import Pipeline


def diarize_audio(audio_path: str) -> list[dict]:
    """Split an audio file into timed speaker segments."""
    try:
        audio, sample_rate = sf.read(audio_path, dtype="float32")
        waveform = torch.from_numpy(audio)

        # soundfile returns (time,) for mono and (time, channel) for stereo.
        # The pipeline expects (channel, time).
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.transpose(0, 1)

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token=os.environ["HF_TOKEN"],
        )
        pipeline.to(torch.device("cpu"))

        output = pipeline({"waveform": waveform, "sample_rate": sample_rate})
        annotation = getattr(output, "speaker_diarization", output)

        speaker_segments = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            speaker_segments.append(
                {
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker,
                }
            )

        return speaker_segments
    except Exception as error:
        raise RuntimeError(
            f"Failed to diarize audio at '{audio_path}': {error}"
        ) from error

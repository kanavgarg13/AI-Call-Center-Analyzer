# Simple manual test for transcribe_audio().
# Replace the placeholder path below with a real .wav / .mp3 / .m4a / .ogg file
# on your computer before running this script.

from transcription import transcribe_audio

# PLACEHOLDER: put the full path to a local audio file here.
audio_path = r"C:\for_project_use\test_audio.mp3"

# This loads the Whisper model (first time can be slow) and turns speech into text.
transcript = transcribe_audio(audio_path)

# Print the full transcript so you can check that transcription worked.
print(transcript)

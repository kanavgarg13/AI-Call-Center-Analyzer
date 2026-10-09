import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(model.name)

client.close()
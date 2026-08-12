import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash-lite")


def generate_text(prompt: str) -> str:
    """Generates text using Gemini."""
    response = model.generate_content(prompt)
    return response.text


def generate_json(prompt: str) -> dict:
    """Generates JSON using Gemini."""
    response = model.generate_content(
        prompt, generation_config={"response_mime_type": "application/json"}
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {}

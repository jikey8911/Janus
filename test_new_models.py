
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_try = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-pro-latest",
    "gemini-2.0-flash"
]

for model in models_to_try:
    print(f"Testing {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents="hi"
        )
        print(f"  ✅ SUCCESS: {model}")
    except Exception as e:
        print(f"  ❌ FAILED: {model} -> {e}")

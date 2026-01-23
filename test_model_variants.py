
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_try = [
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest"
]

for model in models_to_try:
    print(f"Testing {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents="hi"
        )
        print(f"✅ SUCCESS with {model}")
    except Exception as e:
        print(f"❌ FAILED with {model}: {e}")

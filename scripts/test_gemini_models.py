import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "gemini-1.5-flash",
    "models/gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "models/gemini-1.5-flash-001",
    "gemini-1.5-pro",
    "models/gemini-1.5-pro",
    "gemini-pro",
    "models/gemini-pro"
]

print("🚀 Testing Gemini Models...")

for model_name in models_to_test:
    print(f"\n🧪 Testing: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✅ SUCCESS! Response: {response.text[:20]}...")
        # Break on first success? No, let's see all options.
    except Exception as e:
        print(f"❌ Failed: {e}")

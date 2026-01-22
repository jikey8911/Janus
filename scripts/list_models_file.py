import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    models = list(genai.list_models())
    with open("models_list.txt", "w", encoding="utf-8") as f:
        for m in models:
            f.write(f"{m.name}\n")
            f.write(f"  Supported methods: {m.supported_generation_methods}\n")
    print("✅ Models listed to models_list.txt")
except Exception as e:
    print(f"❌ Error listing models: {e}")

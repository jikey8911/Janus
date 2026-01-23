
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("--- Listing and Testing Models ---")
try:
    for m in client.models.list():
        print(f"Model ID: {m.name}")
        # Try it if it has 'generateContent' in supported methods
        if 'generateContent' in m.supported_generation_methods:
             name = m.name.replace('models/', '')
             try:
                 client.models.generate_content(model=name, contents="hi")
                 print(f"  ✅ SUCCESS: {name}")
             except Exception as e:
                 print(f"  ❌ FAILED: {name} -> {e}")
except Exception as e:
    print(f"General error listing/testing: {e}")

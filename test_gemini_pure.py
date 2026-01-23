
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

print(f"Testing key: {api_key[:10]}...")

try:
    # Try different model names
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    for m_name in models_to_try:
        print(f"Trying {m_name}...")
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content("Hola")
            print(f"✅ Success with {m_name}: {response.text}")
            break
        except Exception as e:
            print(f"❌ Failed with {m_name}: {e}")

except Exception as e:
    print(f"Critical error: {e}")

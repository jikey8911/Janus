
import os
import logging
from dotenv import load_dotenv
from groq import Groq

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("TestGroqJSON")

def test_json_mode():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or "your_groq_api_key_here" in api_key:
        logger.error("❌ Groq API Key not set. Please set it in .env to run this test.")
        return

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL_NAME", "llama3-70b-8192")
    
    logger.info(f"Testing JSON mode with model: {model}")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": "Return a JSON object with key 'status' and value 'ok'"}
            ],
            response_format={"type": "json_object"}
        )
        content = completion.choices[0].message.content
        logger.info(f"✅ Success! Response: {content}")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_json_mode()

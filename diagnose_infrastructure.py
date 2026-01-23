
import os
import logging
import json
import socket
from dotenv import load_dotenv
from google import genai
import redis
from pymongo import MongoClient

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("JanusDiagnose")

load_dotenv()

def test_redis():
    logger.info("--- Testing Redis ---")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = redis.from_url(redis_url)
        r.ping()
        logger.info(f"✅ Redis is WORKING at {redis_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Redis is NOT WORKING: {e}")
        return False

def test_mongodb():
    logger.info("--- Testing MongoDB ---")
    db_url = os.getenv("DATABASE_URL")
    try:
        client = MongoClient(db_url)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        logger.info("✅ MongoDB is WORKING")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB is NOT WORKING: {e}")
        return False

def test_gemini():
    logger.info("--- Testing Gemini ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found in .env")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        logger.info("✅ Gemini Client connected.")
        
        logger.info("🔄 Listing available models...")
        models = client.models.list()
        pro_models = [m.name for m in models if 'pro' in m.name.lower()]
        logger.info(f"Available Pro Models: {pro_models}")
        
        # Test generation with gemini configured in .env
        test_model = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro")
        if 'models/gemini-1.5-pro-latest' in pro_models:
            test_model = 'gemini-1.5-pro-latest'
        elif pro_models:
            test_model = pro_models[0].replace('models/', '')

        logger.info(f"🔄 Testing generation with model: {test_model}")
        response = client.models.generate_content(
            model=test_model,
            contents="Say 'Janus is alive' in Spanish"
        )
        logger.info(f"✅ Gemini Response: {response.text}")
        return True, test_model
    except Exception as e:
        logger.error(f"❌ Gemini FAILED: {e}")
        return False, None

def test_freelancer():
    logger.info("--- Testing Freelancer Adapter ---")
    try:
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        adapter = FreelancerAdapter()
        # Simple search test
        jobs = adapter.search_jobs("(python)", limit=1)
        logger.info(f"✅ Freelancer Adapter WORKING. Found {len(jobs)} jobs.")
        return True
    except Exception as e:
        logger.error(f"❌ Freelancer Adapter FAILED: {e}")
        return False

def test_telegram():
    logger.info("--- Testing Telegram Adapter ---")
    try:
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        adapter = TelegramAdapter()
        res = adapter.notify_message("🧪 diagnostic test message from Janus")
        if res:
            logger.info("✅ Telegram Adapter WORKING")
            return True
        else:
            logger.error("❌ Telegram Adapter FAILED to send message")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram Adapter FAILED: {e}")
        return False

def run_diagnostics():
    results = {}
    results['redis'] = test_redis()
    results['mongodb'] = test_mongodb()
    gemini_ok, best_model = test_gemini()
    results['gemini'] = gemini_ok
    results['best_model'] = best_model
    results['freelancer'] = test_freelancer()
    results['telegram'] = test_telegram()
    
    print("\n" + "="*30)
    print("JANUS DIAGNOSTIC SUMMARY")
    print("="*30)
    for service, status in results.items():
        if service == 'best_model': continue
        status_str = "✅ WORKING" if status else "❌ FAILED"
        print(f"{service.capitalize():<12}: {status_str}")
    
    if results['best_model']:
        print(f"\nRecommended Model: {results['best_model']}")
    print("="*30)

if __name__ == "__main__":
    run_diagnostics()

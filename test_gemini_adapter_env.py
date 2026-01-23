
import os
import logging
import json
from dotenv import load_dotenv
from domain.entities import JobOffer
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestGeminiAdapter")

def test_adapter_configuration():
    load_dotenv()
    
    expected_model = os.getenv("GEMINI_MODEL_NAME")
    logger.info(f"🔍 Checking .env configuration...")
    logger.info(f"   GEMINI_MODEL_NAME: {expected_model}")
    
    logger.info("🛠️ Instantiating GeminiAdapter...")
    adapter = GeminiAdapter()
    
    if adapter.model_name != expected_model:
        logger.error(f"❌ Adapter did not load the correct model name. Got: {adapter.model_name}, Expected: {expected_model}")
        return
    else:
        logger.info(f"✅ Adapter initialized with correct model: {adapter.model_name}")

    # Create dummy job
    job = JobOffer(
        external_id="test_env_1",
        title="Python Developer for Automation",
        description="Looking for a Python expert to automate workflows using Selenium and Celery.",
        budget="50-100 USD",
        min_amount=50.0,
        currency="USD"
    )

    logger.info("🚀 Calling analyze_job() ...")
    result = adapter.analyze_job(job)
    
    logger.info("📊 Analysis Result:")
    print(json.dumps(result, indent=2))

    if result.get("score") == 0 and "error" in str(result.get("reasoning", "")).lower():
         logger.warning("⚠️ Analysis failed (likely 429 or 404). Check the reasoning above.")
    elif result.get("score") > 0:
         logger.info("✅ Analysis SUCCESS via Adapter!")

if __name__ == "__main__":
    test_adapter_configuration()

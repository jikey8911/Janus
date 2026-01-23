
import logging
import json
import os
from dotenv import load_dotenv
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("VerifyCategory")

def verify_categorization():
    load_dotenv()
    adapter = GeminiAdapter()
    
    if not adapter.client:
        logger.error("❌ Gemini Client no inicializado.")
        return

    # Caso 1: Software
    job_software = JobOffer(
        external_id="test_cat_1",
        title="Python Scraper for Real Estate",
        description="I need a script to scrape Zillow and save data to MongoDB.",
        budget="500 USD",
        min_amount=500.0,
        currency="USD"
    )

    # Caso 2: Video
    job_video = JobOffer(
        external_id="test_cat_2",
        title="Edit my YouTube Vlog",
        description="Need a video editor for a 10 minute vlog. Cut silence, add music and transitions.",
        budget="100 USD",
        min_amount=100.0,
        currency="USD"
    )

    print("\n--- TEST 1: Software ---")
    res1 = adapter.analyze_job(job_software)
    cat1 = res1.get("category")
    print(f"Title: {job_software.title}")
    print(f"Detected Category: {cat1}")
    
    print("\n--- TEST 2: Video ---")
    res2 = adapter.analyze_job(job_video)
    cat2 = res2.get("category")
    print(f"Title: {job_video.title}")
    print(f"Detected Category: {cat2}")

    # Validaciones
    if cat1 == "desarrollo_software" and cat2 == "video":
        print("\n✅ VERIFICATION SUCCESS: Categories detected correctly.")
    else:
        print("\n❌ VERIFICATION FAILED: Categories do not match expected values (desarrollo_software, video).")

if __name__ == "__main__":
    verify_categorization()

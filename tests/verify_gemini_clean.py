import sys
import os
sys.path.append(os.getcwd())
from dotenv import load_dotenv

load_dotenv()

# Import from the CLEAN adapter file
from infrastructure.adapters.gemini_adapter_v2 import GeminiAdapter
from domain.entities import JobOffer

def test_gemini():
    print("🧪 Testing Gemini Adapter (CLEAN)...")
    
    adapter = GeminiAdapter()
    if not adapter.model:
        print("❌ Gemini Adapter failed to initialize (Check API Key)")
        return

    # Mock Job
    job = JobOffer(
        upwork_id="TEST_JOB_1",
        title="Python Web Scraper Needed",
        description="I need a script to scrape pricing data from e-commerce sites.",
        budget="$200",
        category="Data Scraping"
    )
    
    print(f"📊 Analyzing Job: {job.title}...")
    result = adapter.analyze_job(job)
    
    print("\n📝 Analysis Result:")
    import json
    print(json.dumps(result, indent=2))
    
    if result.get("score") > 0:
        print("\n✅ Verification Successful!")
    else:
        print("\n⚠️ Verification returned low score or error.")

if __name__ == "__main__":
    test_gemini()

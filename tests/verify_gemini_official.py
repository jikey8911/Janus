import os
import sys
import logging
# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.adapters.analyzer.gemini.adapter import GeminiAdapter
from domain.entities import JobOffer
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
# Load .env
load_dotenv()

def main():
    print("--- Starting Gemini Adapter Verification ---")
    
    # Check Env var
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        return

    print(f"API Key found (starts with): {api_key[:5]}...")

    # Instantiate Adapter
    try:
        adapter = GeminiAdapter()
        print("Adapter instantiated successfully.")
    except Exception as e:
        print(f"ERROR: Failed to instantiate adapter: {e}")
        return

    if not adapter.model:
        print("ERROR: Adapter model is None (initialization failed). check logs.")
        return

    # Create dummy job
    job = JobOffer(
        external_id="test_123",
        title="Python Developer for Automation",
        description="Looking for an expert in Python to automate daily tasks using Selenium and APIs.",
        budget="50-100 USD",
        min_amount=50.0,
        currency="USD",
        status="pending",
        category="Development"
    )

    print(f"\nAnalyzing Job: {job.title}")
    
    # Test analyze_job
    try:
        result = adapter.analyze_job(job)
        print("\nAnalysis Result:")
        print(result)
    except Exception as e:
        print(f"\nERROR during analysis: {e}")

    print("\n--- Verification Finished ---")

if __name__ == "__main__":
    main()
import sys
import os
sys.path.append(os.getcwd())
from dotenv import load_dotenv
import logging

# Configure logging to see adapter output
logging.basicConfig(level=logging.INFO)

load_dotenv()

from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter

def main():
    print("🚀 Fetching jobs from Freelancer.com...")
    
    adapter = FreelancerAdapter()
    if not adapter.oauth_token:
        print("❌ Error: FREELANCER_OAUTH_TOKEN not found in .env")
        return

    # Search query
    query = "Python"
    print(f"🔎 Query: {query}")
    
    try:
        jobs = adapter.search_jobs(query)
        
        if not jobs:
            print("⚠️ No jobs found (or API error). Check logs.")
        else:
            print(f"✅ Found {len(jobs)} jobs:")
            for job in jobs:
                print(f"  - [{job.currency} {job.budget}] {job.title} (ID: {job.external_id or job.upwork_id})")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

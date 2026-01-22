import sys
import os
sys.path.append(os.getcwd())

print("Testing dependencies...")
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    print("✅ Requests/Urllib3 deps ok")
except ImportError as e:
    print(f"❌ Dependency missing: {e}")

print("Testing Adapter Import...")
try:
    from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
    print("✅ Adapter Import success")
except Exception as e:
    print(f"❌ Adapter Import failed: {e}")
    import traceback
    traceback.print_exc()

import sys
import os
sys.path.append(os.getcwd())
try:
    from domain.entities import JobOffer
    print("Success importing JobOffer")
except Exception as e:
    print(f"Failed: {e}")

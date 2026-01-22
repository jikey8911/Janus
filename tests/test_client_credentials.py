import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FREELANCER_CLIENT_ID")
CLIENT_SECRET = os.getenv("FREELANCER_CLIENT_SECRET")
TOKEN_URL = "https://accounts.freelancer.com/oauth/token"

print(f"Testing Client Credentials for {CLIENT_ID}...")

payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "basic"
}

try:
    response = requests.post(TOKEN_URL, data=payload)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print("✅ Client Credentials success!")
        print(f"Token: {data.get('access_token')[:20]}...")
        
        # Try to get self
        headers = {"Authorization": f"Bearer {data.get('access_token')}"}
        self_resp = requests.get("https://www.freelancer.com/api/users/0.1/self", headers=headers)
        print(f"Self Status: {self_resp.status_code}")
        print(f"Self Response: {self_resp.text}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

import sys
import os
sys.path.append(os.getcwd())

print("1. Importing JobOffer...")
try:
    from domain.entities import JobOffer
    print("✅ JobOffer success")
except Exception as e:
    print(f"❌ JobOffer failed: {e}")

print("2. Importing Mongo Repos...")
try:
    from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
    print("✅ Mongo Repos success")
except Exception as e:
    print(f"❌ Mongo Repos failed: {e}")

print("3. Importing UpworkAdapter...")
try:
    from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
    print("✅ UpworkAdapter success")
except Exception as e:
    print(f"❌ UpworkAdapter failed: {e}")

print("4. Importing TelegramAdapter...")
try:
    from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
    print("✅ TelegramAdapter success")
except Exception as e:
    print(f"❌ TelegramAdapter failed: {e}")

print("5. Importing OpenAIAdapter...")
try:
    from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
    print("✅ OpenAIAdapter success")
except Exception as e:
    print(f"❌ OpenAIAdapter failed: {e}")

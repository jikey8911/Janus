import os
import logging
import google.generativeai as genai
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# INLINE ENTITIES
@dataclass
class JobOffer:
    upwork_id: str
    title: str
    description: str
    budget: str
    category: str = "General"

# INLINE ADAPTER
class GeminiAdapter:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("❌ GEMINI_API_KEY not found in env.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('models/gemini-1.5-flash')
                print(f"✅ Gemini configured with Key: {self.api_key[:5]}...")
            except Exception as e:
                print(f"❌ Error configuring Gemini: {e}")
                self.model = None

    def analyze_job(self, job: JobOffer) -> dict:
        if not self.model:
            return {"score": 0, "reasoning": "Gemini client not initialized"}

        prompt = f"""
        Actúa como un experto consultor.
        Analiza esta oferta:
        {job.title}
        {job.description}
        {job.budget}
        
        Output JSON:
        {{
            "score": (0-100),
            "viability_analysis": "string",
            "key_risks": [],
            "recommended_stack": [],
            "research_topics": []
        }}
        """
        
        try:
            print("⏳ Sending request to Gemini...")
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Error analyzing with Gemini: {e}")
            return {"score": 0, "reasoning": str(e)}

def run_test():
    print("🚀 Starting Root Monolith Test for Gemini")
    adapter = GeminiAdapter()
    
    if adapter.model:
        job = JobOffer(
            upwork_id="TEST",
            title="Simple Python Script",
            description="Write a hello world script",
            budget="$50"
        )
        result = adapter.analyze_job(job)
        print("\n📝 Result:")
        print(result)
    else:
        print("⏭️ Skipping analysis due to init failure.")

if __name__ == "__main__":
    run_test()

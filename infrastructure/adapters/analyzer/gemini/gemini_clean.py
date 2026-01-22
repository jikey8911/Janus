import os
import logging
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage
import google.generativeai as genai

class GeminiAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY not found.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

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
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            import json
            return json.loads(response.text)
        except Exception as e:
            logging.error(f"Error analyzing with Gemini: {e}")
            return {"score": 0, "reasoning": str(e)}

    def suggest_reply(self, message: ClientMessage) -> str:
        return ""

    def generate_proposal_content(self, job: JobOffer) -> str:
        return ""

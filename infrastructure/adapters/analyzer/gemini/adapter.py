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
            # Usamos Gemini 1.5 Flash por su velocidad y bajo costo para diagnóstico
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            # self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Opcional si está disponible

    def analyze_job(self, job: JobOffer) -> dict:
        """
        Realiza un diagnóstico rápido de la oferta usando Gemini Flash.
        """
        if not self.model:
            return {"score": 0, "reasoning": "Gemini client not initialized"}

        prompt = f"""
        Actúa como un experto consultor de freelancing (Janus).
        Analiza esta oferta de trabajo y genera un diagnóstico JSON:

        Job Title: {job.title}
        Description: {job.description}
        Budget: {job.budget}
        
        Output JSON:
        {{
            "score": (0-100),
            "viability_analysis": "Breve análisis de viabilidad técnica y económica (1 frase)",
            "key_risks": ["Riesgo 1", "Riesgo 2"],
            "recommended_stack": ["Tech A", "Tech B"],
            "research_topics": ["Tema a investigar 1", "Tema a investigar 2"]
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
        # Implementación simple o delegar a OpenAI si se prefiere
        pass

    def generate_proposal_content(self, job: JobOffer) -> str:
        # Implementación simple o delegar a OpenAI si se prefiere
        pass

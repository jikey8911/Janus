import os
import logging
import json
from typing import List
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage
import google.generativeai as genai

class GeminiAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY no encontrada en las variables de entorno.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Usamos 2.5 Flash para mayor velocidad y disponibilidad confirmada
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                logging.error(f"Error al configurar Gemini: {e}")
                self.model = None

    def analyze_job(self, job: JobOffer) -> dict:
        if not self.model:
            return {"score": 0, "reasoning": "Cliente Gemini no inicializado"}

        prompt = f"""
        Actúa como un experto consultor de software freelance.
        Analiza esta oferta de trabajo:
        
        Título: {job.title}
        Descripción: {job.description}
        Presupuesto: {job.budget}
        
        Provee una respuesta estrictamente en JSON con este formato:
        {{
            "score": (0-100 entero, probabilidad de éxito basada en claridad y presupuesto),
            "viability_analysis": "Breve análisis (1 frase)",
            "key_risks": ["riesgo1", "riesgo2"],
            "recommended_stack": ["tech1", "tech2"],
            "research_topics": ["tema1"]
        }}
        """
        
        try:
            # Forzamos respuesta tipo JSON
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logging.error(f"Error analizando con Gemini: {e}")
            return {"score": 0, "reasoning": str(e)}

    def generate_proposal_content(self, job: JobOffer) -> str:
        """Genera el texto de la propuesta para enviar a Freelancer."""
        if not self.model:
            return "Interesado en el proyecto."

        prompt = f"""
        Escribe una propuesta profesional y persuasiva para el siguiente proyecto:
        Título: {job.title}
        Descripción: {job.description}
        
        Instrucciones:
        1. Sé breve y directo (máximo 150 palabras).
        2. Enfócate en cómo resolverás el problema.
        3. No uses saludos genéricos como 'Hola, he leído tu proyecto'. 
        4. Escribe en el idioma en que está la oferta (Inglés o Español).
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error generando propuesta: {e}")
            return f"Hola, estoy muy interesado en ayudarte con {job.title}. Tengo experiencia en proyectos similares."

    def suggest_reply(self, message: ClientMessage) -> str:
        """Sugerencia de respuesta a un mensaje directo del cliente."""
        # Implementación básica para chat
        return "Gracias por tu mensaje. Estoy revisando los detalles."
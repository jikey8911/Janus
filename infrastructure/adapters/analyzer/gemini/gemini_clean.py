import os
import logging
import json
from typing import Dict, Any
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage
from google import genai
from google.genai import types

class GeminiAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY no encontrada.")
            self.model = None
        else:
            try:
                # Usamos el nuevo SDK google-genai
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-1.5-pro'
            except Exception as e:
                logging.error(f"Error configurando Gemini: {e}")
                self.client = None

    def analyze_job(self, job: JobOffer) -> Dict[str, Any]:
        """Analiza la viabilidad de una oferta de Freelancer."""
        if not self.client:
            return {"score": 0, "reasoning": "Gemini client not initialized"}

        prompt = f"""
        Actúa como un experto consultor técnico freelance. 
        Analiza detalladamente esta oferta de trabajo para determinar si vale la pena aplicar (Aprobar) o no (Rechazar):
        
        Título: {job.title}
        Descripción: {job.description}
        Presupuesto: {job.budget}
        
        Devuelve estrictamente un objeto JSON con esta estructura:
        {{
            "score": (entero del 0 al 100),
            "decision": ("approved" si la oportunidad es buena, "rejected" si no lo es),
            "viability": "un párrafo corto explicando por qué es o no una buena oportunidad",
            "key_risks": ["riesgo 1", "riesgo 2"],
            "recommended_stack": ["tecnología 1", "tecnología 2"],
            "research_topics": ["punto a investigar antes de ofertar"],
            "suggested_bid": (monto numérico sugerido para ofertar basado en el presupuesto y complejidad)
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            analysis_res = json.loads(response.text)
            logging.info(f"Gemini Analysis Output: {analysis_res}")
            return analysis_res
        except Exception as e:
            logging.error(f"Error en analyze_job: {e}")
            return {"score": 0, "reasoning": f"Error de análisis: {str(e)}"}

    def generate_proposal_content(self, job: JobOffer) -> str:
        """Genera el texto de la propuesta (bid) para Freelancer.com."""
        if not self.client:
            return "Hola, estoy interesado en tu proyecto y tengo la experiencia necesaria para ayudarte."

        prompt = f"""
        Escribe una propuesta de bid corta, profesional y directa para este proyecto en Freelancer.com:
        Proyecto: {job.title}
        Descripción: {job.description}

        Requisitos de la propuesta:
        1. NO uses saludos genéricos como 'Dear Hiring Manager'. 
        2. Ve directo al grano sobre cómo resolverás el problema técnico.
        3. Mantén el idioma original de la oferta (si es inglés, escribe en inglés).
        4. Máximo 400 caracteres.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error generando propuesta: {e}")
            return f"He revisado tu proyecto '{job.title}' y me gustaría ayudarte. Tengo experiencia previa en tareas similares."

    def suggest_reply(self, message: ClientMessage) -> str:
        """Sugiere una respuesta para el chat con el cliente."""
        if not self.client:
            return "Gracias por tu mensaje. Lo revisaré pronto."

        prompt = f"""
        Como asistente experto de gestión de proyectos, sugiere una respuesta para este mensaje de un cliente:
        De: {message.client_name}
        Mensaje del cliente: "{message.message_content}"
        Contexto del proyecto: {message.job_context}
        
        La respuesta debe ser profesional, servicial y mantener el interés del cliente.
        Responde en el mismo idioma que el cliente.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error sugiriendo respuesta: {e}")
            return "Entendido. ¿Podrías darme más detalles al respecto?"
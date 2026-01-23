
import os
import logging
import json
from typing import Dict, Any
from groq import Groq
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage

class GroqAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logging.warning("GROQ_API_KEY no encontrada.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                self.model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
            except Exception as e:
                logging.error(f"Error configurando Groq: {e}")
                self.client = None

    def analyze_job(self, job: JobOffer) -> Dict[str, Any]:
        """Analiza la viabilidad de una oferta usando Groq (Llama 3)."""
        if not self.client:
            return {"score": 0, "reasoning": "Groq client not initialized"}

        prompt = f"""
        Actúa como un experto consultor técnico freelance. 
        Analiza esta oferta para determinar si vale la pena aplicar:
        
        Título: {job.title}
        Descripción: {job.description}
        Presupuesto: {job.budget}
        
        Devuelve estrictamente un objeto JSON con esta estructura:
        {{
            "score": (entero 0-100),
            "decision": ("approved" o "rejected"),
            "viability": "breve analisis",
            "key_risks": ["riesgo 1", "riesgo 2"],
            "recommended_stack": ["tech 1", "tech 2"],
            "research_topics": ["tema 1"],
            "suggested_bid": (numero),
            "category": (una de: "audio", "video", "texto", "transcripcion", "diseno", "electronica", "desarrollo_software")
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful JSON assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error en analyze_job (Groq): {e}")
            return {"score": 0, "reasoning": str(e)}

    def generate_proposal_content(self, job: JobOffer) -> str:
        if not self.client:
            return "Propuesta genérica por falta de cliente Groq."

        prompt = f"""
        Escribe una propuesta profesional para Freelancer.com:
        Proyecto: {job.title}
        Descripción: {job.description}
        
        Reglas: Directo, sin saludos genéricos, max 400 chars, idioma original de la oferta.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generando propuesta (Groq): {e}")
            return "Error generando propuesta."

    def suggest_reply(self, message: ClientMessage) -> str:
        if not self.client:
            return "Gracias."

        prompt = f"""
        Sugiere respuesta para cliente: "{message.message_content}"
        Contexto: {message.job_context}
        Profesional y conciso.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error sugiriendo respuesta (Groq): {e}")
            return "Error generando respuesta."

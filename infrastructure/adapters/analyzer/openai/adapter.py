import os
import logging
import json
from openai import OpenAI
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage

class OpenAIAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def analyze_job(self, job: JobOffer) -> dict:
        """
        Analiza una oferta de trabajo usando OpenAI.
        Incluye cálculo de monto sugerido y análisis de viabilidad.
        """
        if not self.client:
            return {"score": 0, "reasoning": "OpenAI Client no inicializado"}

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
            "research_topics": ["tema1"],
            "suggested_bid": (monto numérico sugerido para ofertar basado en el presupuesto y complejidad)
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un consultor experto que responde solo en JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error analizando con OpenAI: {e}")
            return {"score": 0, "reasoning": str(e)}

    def generate_proposal_content(self, job: JobOffer) -> str:
        """Genera el texto de la propuesta profesional para enviar al cliente."""
        if not self.client:
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un redactor Senior de propuestas freelancing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generando propuesta con OpenAI: {e}")
            return f"Hola, estoy muy interesado en ayudarte con {job.title}. Tengo experiencia en proyectos similares."

    def suggest_reply(self, message: ClientMessage) -> str:
        """Sugerencia de respuesta a un mensaje directo del cliente."""
        if not self.client:
            return "Gracias por tu mensaje. Lo revisaré pronto."

        prompt = f"""
        Como asistente experto, sugiere una respuesta para este mensaje de un cliente:
        De: {message.client_name}
        Mensaje: {message.message_content}
        Contexto del proyecto: {message.job_context}
        
        La respuesta debe ser profesional, servicial y mantener el interés del cliente.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un Project Manager experto en comunicación con clientes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error sugiriendo respuesta con OpenAI: {e}")
            return "Gracias por contactarme. Estoy revisando los detalles y te responderé en breve."

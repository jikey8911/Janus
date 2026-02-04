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
                self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro")
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
            "suggested_bid": (monto numérico sugerido para ofertar basado en el presupuesto y complejidad),
            "category": (una de las siguientes: "audio", "video", "texto", "transcripcion", "diseno", "electronica", "desarrollo_software")
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
        Actúa como un desarrollador Senior freelance altamente eficiente.
        Tu objetivo es ganar este proyecto en Freelancer.com escribiendo una propuesta irresistible y técnica.

        DETALLES DEL PROYECTO:
        Título: {job.title}
        Descripción: {job.description}

        INSTRUCCIONES DE REDACCIÓN:
        1. ANÁLISIS TÉCNICO: Identifica las tecnologías clave mencionadas (o implícitas) en la descripción y MENCIONALAS explícitamente en tu propuesta para demostrar que leíste los requisitos.
        2. SOLUCIÓN DIRECTA: No saludes genéricamente. Empieza diciendo CÓMO vas a resolver su problema específico.
        3. AUTORIDAD: Menciona brevemente experiencia relevante con esas tecnologías específicas.
        4. CALL TO ACTION: Termina invitando a conversar para definir detalles o mostrar demos previos.
        5. IDIOMA: Escribe estrictamente en el mismo idioma de la descripción del proyecto (Inglés o Español).
        6. LONGITUD: Manténlo conciso (max 1000 caracteres), profesional y sin relleno.
        
        EJEMPLO DE ESTRUCTURA (Adáptalo al idioma):
        "Hola, puedo construir tu [sistema] usando [tecnología A] y [tecnología B]. He desarrollado proyectos similares como... Mi enfoque sería..."
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
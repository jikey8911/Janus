import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o" # O gpt-4.1-mini según disponibilidad

    def analyze_job_and_generate_proposal(self, job_title, job_description):
        prompt = f"""
        Actúa como un experto en Upwork y automatización de flujos de trabajo con IA.
        Analiza la siguiente oferta de trabajo y genera una propuesta persuasiva.
        
        Título: {job_title}
        Descripción: {job_description}
        
        Tu respuesta debe ser un JSON con este formato:
        {{
            "score": 0-100,
            "analysis": "Breve análisis de por qué es buena o no",
            "proposal": "Texto completo de la propuesta personalizada"
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content

    def suggest_message_response(self, client_message, job_context):
        prompt = f"""
        El cliente me ha enviado este mensaje en Upwork: "{client_message}"
        Contexto del trabajo: {job_context}
        
        Genera una respuesta profesional y estratégica que mantenga el interés del cliente y avance en la negociación.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

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
        if not self.client: return {"score": 0, "reasoning": "No Client"}
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": f"Analyze {job.title}"}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
             return {"score": 0}

    def suggest_reply(self, message: ClientMessage) -> str:
        return "Reply"

    def generate_proposal_content(self, job: JobOffer) -> str:
        return "Proposal"

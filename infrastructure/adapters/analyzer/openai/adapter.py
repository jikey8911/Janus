import os
import logging
import json
from typing import Optional
from openai import OpenAI
from domain.ports import AIServicePort
from domain.entities import JobOffer, ClientMessage

class OpenAIAdapter(AIServicePort):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY not found. OpenAIAdapter will fail.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def analyze_job(self, job: JobOffer) -> dict:
        if not self.client:
            return {"score": 0, "reasoning": "OpenAI client not initialized"}

        prompt = f"""
        Analyze the following Upwork job offer and provide a JSON response with:
        - score: 0 to 100 integer indicating viability (100 is best).
        - pros: list of strings.
        - cons: list of strings.
        - reasoning: brief explanation.

        Job Title: {job.title}
        Description: {job.description}
        Budget: {job.budget}
        Category: {job.category}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert freelancer assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logging.error(f"Error analyzing job with OpenAI: {e}")
            return {"score": 0, "reasoning": f"Error: {str(e)}"}

    def suggest_reply(self, message: ClientMessage) -> str:
        if not self.client:
            return "Error: OpenAI client not initialized"

        prompt = f"""
        Draft a professional and persuasive reply to this client message on Upwork.
        
        Client Name: {message.client_name}
        Message: {message.message_content}
        Context (Job): {message.job_context}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert freelancer assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error suggesting reply with OpenAI: {e}")
            return "Error generating reply."

    def generate_proposal_content(self, job: JobOffer) -> str:
        if not self.client:
            return "Error: OpenAI client not initialized"

        prompt = f"""
        Write a winning Upwork cover letter for the following job. 
        Focus on value proposition, professionalism, and relevance.
        Keep it concise (under 200 words if possible).

        Job Title: {job.title}
        Description: {job.description}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a top-rated freelancer copywriter."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generating proposal with OpenAI: {e}")
            return "Error generating proposal."

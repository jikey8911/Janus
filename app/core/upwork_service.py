import upwork
import os

class UpworkService:
    def __init__(self):
        self.config = {
            "consumer_key": os.getenv("UPWORK_CONSUMER_KEY"),
            "consumer_secret": os.getenv("UPWORK_CONSUMER_SECRET"),
            "access_token": os.getenv("UPWORK_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("UPWORK_ACCESS_TOKEN_SECRET")
        }
        self.client = upwork.Client(self.config)

    def search_jobs(self, query='(python OR automation OR ai)'):
        params = {
            'q': query,
            'sort': 'create_time desc',
            'job_status': 'open'
        }
        results = self.client.provider_v2.search_jobs(params)
        return results.get('jobs', [])

    def submit_proposal(self, job_id, proposal_text):
        # Nota: La API de Upwork para enviar propuestas requiere permisos específicos
        # Este es un placeholder para la implementación real
        print(f"Enviando propuesta a {job_id}: {proposal_text[:50]}...")
        return True

from domain.ports import JobRepository, ProposalRepository, UpworkPort, AIServicePort, NotificationPort
from domain.entities import JobOffer, Proposal

class ScanAndAnalyzeJobsUseCase:
    def __init__(
        self, 
        upwork_port: UpworkPort, 
        job_repo: JobRepository, 
        ai_port: AIServicePort, 
        notification_port: NotificationPort
    ):
        self.upwork_port = upwork_port
        self.job_repo = job_repo
        self.ai_port = ai_port
        self.notification_port = notification_port

    def execute(self, query: str = "(python OR automation OR ai)"):
        jobs = self.upwork_port.search_jobs(query)
        for job in jobs:
            existing_job = self.job_repo.get_by_upwork_id(job.upwork_id)
            if not existing_job:
                saved_job = self.job_repo.save(job)
                analysis = self.ai_port.analyze_job(saved_job)
                self.notification_port.notify_opportunity(saved_job, analysis)

class SubmitProposalUseCase:
    def __init__(
        self, 
        upwork_port: UpworkPort, 
        proposal_repo: ProposalRepository,
        notification_port: NotificationPort
    ):
        self.upwork_port = upwork_port
        self.proposal_repo = proposal_repo
        self.notification_port = notification_port

    def execute(self, job_upwork_id: str, content: str):
        success = self.upwork_port.submit_proposal(job_upwork_id, content)
        if success:
            # Aquí se guardaría la propuesta en el repo si fuera necesario
            self.notification_port.notify_message(f"Propuesta enviada con éxito para {job_upwork_id}")
        return success

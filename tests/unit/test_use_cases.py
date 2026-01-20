import unittest
from unittest.mock import MagicMock
from domain.entities import JobOffer, Proposal
from application.use_cases import ScanAndAnalyzeJobsUseCase, GenerateProposalUseCase

class TestScanAndAnalyzeJobsUseCase(unittest.TestCase):
    def setUp(self):
        self.upwork_port = MagicMock()
        self.job_repo = MagicMock()
        self.ai_port = MagicMock()
        self.notification_port = MagicMock()
        
        self.use_case = ScanAndAnalyzeJobsUseCase(
            self.upwork_port,
            self.job_repo,
            self.ai_port,
            self.notification_port
        )

    def test_execute_happy_path_new_job(self):
        # Setup
        job = JobOffer(upwork_id="123", title="Python Dev", description="Code python", budget="100")
        self.upwork_port.search_jobs.return_value = [job]
        self.job_repo.get_by_upwork_id.return_value = None # No existe
        self.job_repo.save.return_value = job
        self.ai_port.analyze_job.return_value = {"score": 90}
        
        # Execute
        self.use_case.execute()
        
        # Assert
        self.upwork_port.search_jobs.assert_called_once()
        self.job_repo.save.assert_called_with(job)
        self.ai_port.analyze_job.assert_called_with(job)
        self.notification_port.notify_opportunity.assert_called_with(job, {"score": 90})

    def test_execute_existing_job(self):
        # Setup
        job = JobOffer(upwork_id="123", title="Python Dev", description="Code python", budget="100")
        self.upwork_port.search_jobs.return_value = [job]
        self.job_repo.get_by_upwork_id.return_value = job # Ya existe
        
        # Execute
        self.use_case.execute()
        
        # Assert
        self.job_repo.save.assert_not_called()
        self.ai_port.analyze_job.assert_not_called()
        self.notification_port.notify_opportunity.assert_not_called()

    def test_execute_upwork_error_handled(self):
        # Setup
        self.upwork_port.search_jobs.side_effect = Exception("API Error")
        
        # Execute (should not raise exception due to try/except)
        self.use_case.execute()
        
        # Assert is verified by not failing

    def test_execute_analysis_error_handled(self):
        # Setup
        job = JobOffer(upwork_id="123", title="Python Dev", description="Code python", budget="100")
        self.upwork_port.search_jobs.return_value = [job]
        self.job_repo.get_by_upwork_id.return_value = None
        self.job_repo.save.return_value = job
        self.ai_port.analyze_job.side_effect = Exception("AI Error")
        
        # Execute
        self.use_case.execute()
        
        # Assert
        self.job_repo.save.assert_called()
        self.notification_port.notify_opportunity.assert_not_called()

        self.job_repo.save.assert_called()
        self.notification_port.notify_opportunity.assert_not_called()

class TestGenerateProposalUseCase(unittest.TestCase):
    def setUp(self):
        self.job_repo = MagicMock()
        self.proposal_repo = MagicMock()
        self.ai_port = MagicMock()
        self.notification_port = MagicMock()
        
        self.use_case = GenerateProposalUseCase(
            self.job_repo,
            self.proposal_repo,
            self.ai_port,
            self.notification_port
        )

    def test_execute_success(self):
        # Setup
        job = JobOffer(id=1, upwork_id="123", title="Python Dev", description="Desc", budget="100")
        self.job_repo.get_by_upwork_id.return_value = job
        self.ai_port.generate_proposal_content.return_value = "Hola, soy el mejor."
        
        saved_proposal = Proposal(id=10, job_offer_id=1, content="Hola, soy el mejor.", status="draft")
        self.proposal_repo.save.return_value = saved_proposal
        
        # Execute
        result = self.use_case.execute("123")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.content, "Hola, soy el mejor.")
        self.proposal_repo.save.assert_called_once()
        self.ai_port.generate_proposal_content.assert_called_with(job)
        self.notification_port.notify_message.assert_called_once()

    def test_execute_job_not_found(self):
        self.job_repo.get_by_upwork_id.return_value = None
        
        result = self.use_case.execute("123")
        
        self.assertIsNone(result)
        self.proposal_repo.save.assert_not_called()
        self.notification_port.notify_message.assert_not_called()

    def test_execute_ai_error(self):
        job = JobOffer(id=1, upwork_id="123", title="Python Dev", description="Desc", budget="100")
        self.job_repo.get_by_upwork_id.return_value = job
        self.ai_port.generate_proposal_content.side_effect = Exception("AI Fail")
        
        result = self.use_case.execute("123")
        
        self.assertIsNone(result)
        self.proposal_repo.save.assert_not_called()
        self.notification_port.notify_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()

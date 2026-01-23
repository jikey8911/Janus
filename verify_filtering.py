
import unittest
from unittest.mock import MagicMock
from application.use_cases import ScanAndAnalyzeJobsUseCase
from domain.entities import JobOffer

class TestNotificationFiltering(unittest.TestCase):
    def test_filtering_and_summary(self):
        # Mocks
        mock_platform = MagicMock()
        mock_job_repo = MagicMock()
        mock_ai = MagicMock()
        mock_notifier = MagicMock()

        # Configurar UseCase
        use_case = ScanAndAnalyzeJobsUseCase(
            platform_port=mock_platform,
            job_repo=mock_job_repo,
            ai_port=mock_ai,
            notification_port=mock_notifier
        )

        # 1. Simular ofertas encontradas
        job1 = JobOffer(external_id="1", title="Job 1 (High Score)", description="desc", budget="100", min_amount=100, currency="USD")
        job2 = JobOffer(external_id="2", title="Job 2 (Low Score)", description="desc", budget="100", min_amount=100, currency="USD")
        job3 = JobOffer(external_id="3", title="Job 3 (High Score)", description="desc", budget="100", min_amount=100, currency="USD")
        
        # Simular search_jobs devolviendo estos 3
        mock_platform.search_jobs.return_value = [job1, job2, job3]

        # Simular repositorio (no existen en DB)
        mock_job_repo.get_by_external_id.return_value = None
        mock_job_repo.save.side_effect = lambda x: x # devuelve el mismo objeto

        # 2. Simular Análisis IA
        # Job 1: Score 85 (>60) -> Approved
        # Job 2: Score 40 (<=60) -> Rejected
        # Job 3: Score 65 (>60) -> Approved
        mock_ai.analyze_job.side_effect = [
            {"score": 85, "decision": "approved", "category": "dev"},
            {"score": 40, "decision": "rejected", "category": "dev"},
            {"score": 65, "decision": "approved", "category": "dev"}
        ]

        # 3. Ejecutar
        print("⚡ Ejecutando Use Case con Mocks...")
        use_case.execute(limit=3)

        # 4. Validaciones
        
        # notify_opportunity debe llamarse SOLO 2 veces (Job 1 y Job 3)
        self.assertEqual(mock_notifier.notify_opportunity.call_count, 2, "Debería notificar solo 2 oportunidades (score > 60)")
        
        # Verificar argumentos de las llamadas
        calls = mock_notifier.notify_opportunity.call_args_list
        scores_notified = [c[0][1]['score'] for c in calls] # analysis is 2nd arg
        print(f"Scores notificados: {scores_notified}")
        self.assertIn(85, scores_notified)
        self.assertIn(65, scores_notified)
        self.assertNotIn(40, scores_notified)

        # notify_message debe llamarse al menos 1 vez (el resumen)
        # Verificamos que el último mensaje contenga el resumen esperado
        last_call_args = mock_notifier.notify_message.call_args
        summary_msg = last_call_args[0][0]
        print(f"Mensaje Resumen: {summary_msg}")
        
        self.assertIn("Ofertas Analizadas: 3", summary_msg)
        self.assertIn("Aprobadas (>60): 2", summary_msg)
        
        print("✅ TEST PASSED: Filtering and Summary logic is correct.")

if __name__ == "__main__":
    unittest.main()

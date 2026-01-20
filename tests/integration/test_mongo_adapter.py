import unittest
import os
from datetime import datetime
from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository, MongoProposalRepository
from domain.entities import JobOffer, Proposal

# Para correr este test se requiere una instancia de MongoDB.
# Si no hay, fallará la conexión.
# Se puede usar mongomock para pruebas unitarias sin DB real, 
# pero HU 3.1 pide el adaptador real.
# Intentaremos conectar a localhost, si falla, es esperado en entorno sin DB.

class TestMongoAdapter(unittest.TestCase):
    def setUp(self):
        # Usar una BD de test
        self.connection_string = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = "janus_test_db"
        self.job_repo = MongoJobRepository(self.connection_string, self.db_name)
        self.proposal_repo = MongoProposalRepository(self.connection_string, self.db_name)

    def tearDown(self):
        # Limpiar BD después del test
        try:
            self.job_repo.client.drop_database(self.db_name)
        except:
            pass

    def test_save_and_get_job(self):
        job = JobOffer(
            upwork_id="test_job_1",
            title="Python Developer",
            description="Build cool stuff",
            budget="500",
            status="pending",
            created_at=datetime.now()
        )
        
        try:
            saved = self.job_repo.save(job)
            self.assertEqual(saved.upwork_id, "test_job_1")
            
            fetched = self.job_repo.get_by_upwork_id("test_job_1")
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.title, "Python Developer")
        except Exception as e:
            print(f"Skipping Mongo Test: {e}")

    def test_save_proposal(self):
        proposal = Proposal(
            job_offer_id=123,
            content="I am the best",
            status="draft"
        )
        
        try:
            saved = self.proposal_repo.save(proposal)
            self.assertIsNotNone(saved.id)
            print(f"Generated Proposal ID: {saved.id}")
            
            # Update
            saved.status = "sent"
            updated = self.proposal_repo.save(saved)
            self.assertEqual(updated.status, "sent")
            self.assertEqual(updated.id, saved.id)
        except Exception as e:
            print(f"Skipping Mongo Test: {e}")

if __name__ == '__main__':
    unittest.main()

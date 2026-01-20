from domain.ports import FreelancePlatformPort
from infrastructure.adapters.platforms.upwork.adapter import UpworkAdapter
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.entrypoints.celery_tasks import scan_jobs_task
from infrastructure.adapters.workers.base import MultimediaWorkerPort

def verify_refactor():
    print("Verifying Port Renaming...")
    assert issubclass(UpworkAdapter, FreelancePlatformPort)
    assert issubclass(FreelancerAdapter, FreelancePlatformPort)
    print("Adapters correctly inherit from FreelancePlatformPort.")
    
    print("Verifying Worker Interface...")
    assert hasattr(MultimediaWorkerPort, 'generate_content')
    print("Worker Interface verified.")

    print("Verifying Celery Task Import...")
    # Just checking if we can import it without errors (dependencies resolved)
    print("Celery Task module imported.")

if __name__ == "__main__":
    verify_refactor()

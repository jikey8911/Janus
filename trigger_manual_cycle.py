
import logging
import asyncio
import os
from dotenv import load_dotenv

# Adapters
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from infrastructure.adapters.persistence.mongodb.adapter import MongoProposalRepository, MongoJobRepository, MongoEventCheckpointRepository

# Use Cases
from application.use_cases import ScanAndAnalyzeJobsUseCase

# Config logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ManualTrigger")

async def run_manual_scan():
    load_dotenv()
    logger.info("🚀 Starting Manual System Trigger...")
    
    # 1. Instantiate Adapters
    platform_adapter = FreelancerAdapter()
    ai_adapter = GeminiAdapter()
    notification_adapter = TelegramAdapter()
    
    # Repos
    proposal_repo = MongoProposalRepository()
    job_repo = MongoJobRepository()
    
    # 2. Instantiate Use Case
    use_case = ScanAndAnalyzeJobsUseCase(
        platform_port=platform_adapter,
        job_repo=job_repo,
        ai_port=ai_adapter,
        notification_port=notification_adapter
    )
    
    # 3. Execute
    logger.info("⚡ Executing ScanAndAnalyzeJobsUseCase...")
    try:
        # We use a query likely to return results to force activity
        await use_case.execute(query="(python) AND (automation OR bot OR script)", limit=3)
        logger.info("✅ Manual execution completed successfully.")
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_manual_scan())

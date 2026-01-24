import sys
import os

# Add root to path to ensure imports work
sys.path.append(os.getcwd())

from infrastructure.entrypoints.celery_tasks import scan_jobs_task

if __name__ == "__main__":
    print("🚀 Triggering initial job scan (Direct Execution Mode)...")
    try:
        # Ejecutar DIRECTAMENTE la función (bypass Celery Broker)
        # Esto evita problemas de conexión (WinError 10061) si Redis/Worker no están listos.
        # Al ser un script separado (subprocess), no bloquea el hilo principal.
        scan_jobs_task(query="", limit=10)
        print("✅ Direct execution of 'scan_jobs_task' completed.")
    except Exception as e:
        print(f"❌ Failed to run direct task: {e}")
        import traceback
        traceback.print_exc()

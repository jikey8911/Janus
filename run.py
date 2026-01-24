import subprocess
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

def run_services():
    print("🚀 Starting Janus V2.1 Services...")
    
    processes = []
    
    # Configurar environment para incluir el directorio actual
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # 1. Telegram Bot
    print("🤖 Launching Telegram Bot...")
    bot_process = subprocess.Popen([sys.executable, "infrastructure/entrypoints/telegram_bot.py"], env=env)
    processes.append(bot_process)
    
    # 2. Celery Worker
    print("🧠 Launching Celery Worker...")
    # On Windows we use 'solo' pool or 'spawn' usually, but 'solo' is safer for simple dev
    # Use sys.executable -m celery to ensure we use the same python environment
    worker_cmd = [sys.executable, "-m", "celery", "-A", "infrastructure.celery_app", "worker", "--loglevel=info", "--pool=solo"]
    worker_process = subprocess.Popen(worker_cmd, env=env)
    processes.append(worker_process)
    
    # 3. Celery Beat
    print("⏱️ Launching Celery Beat...")
    beat_cmd = [sys.executable, "-m", "celery", "-A", "infrastructure.celery_app", "beat", "--loglevel=info"]
    beat_process = subprocess.Popen(beat_cmd, env=env)
    processes.append(beat_process)
    
    print("\n✅ All services started. Press Ctrl+C to stop.")

    # 4. Trigger Initial Job Scan (Direct Mode)
    print("🚀 Triggering initial job scan (Direct Mode)...")
    # time.sleep(5) # No wait needed for direct execution
    subprocess.Popen([sys.executable, "infrastructure/trigger_initial_task.py"], env=env)
    
    try:
        while True:
            time.sleep(1)
            # Check if any process has died
            for p in processes:
                if p.poll() is not None:
                    print(f"❌ A service has stopped unexpectedly (PID: {p.pid}). Stopping all...")
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for p in processes:
            p.terminate()
            p.wait()
        print("Done.")

if __name__ == "__main__":
    run_services()

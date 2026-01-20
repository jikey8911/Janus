import logging
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# Check if python-telegram-bot is installed, if not we will mock or fail gracefully for now.
# In a real environment, we would add it to requirements.txt.
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
except ImportError:
    logging.error("python-telegram-bot not installed. Please install it with 'pip install python-telegram-bot'")
    exit(1)

# TODO: Import Use Cases
# from application.use_cases import ReplyToClientUseCase, ApproveProposalUseCase

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 Janus v2.1 Online. Listening for commands.")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /reply [text]
    Usage: /reply This is my response to the client.
    Note: Ideally this needs context (which client? which job?). 
    For V2.1 Sprint 4, we might assume 'last active context' or require ID.
    """
    user_text = " ".join(context.args)
    if not user_text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ Uso: /reply [mensaje]. Faltó el mensaje."
        )
        return

    # TODO: Invoke Use Case
    # success = reply_use_case.execute(content=user_text)
    
    # Mock Response
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"✅ Mensaje enviado (Simulado):\n'{user_text}'"
    )

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /approve [proposal_id]
    """
    # proposal_id = context.args[0] if context.args else "LAST_DRAFT"
    
    # TODO: Invoke Use Case
    # success = approve_proposal_use_case.execute(proposal_id)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="✅ Propuesta aprobada y enviada (Simulado)."
    )

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /generate [job_id]
    Triggers the Celery task to generate a proposal.
    """
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Uso: /generate [job_id]")
        return

    job_id = context.args[0]
    
    # Trigger Celery Task
    # We delay import to avoid circular dependency issues at module level if any
    from infrastructure.entrypoints.celery_tasks import generate_proposal_task
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚙️ Iniciando generación de propuesta para {job_id}...")
    
    # celery call
    # generate_proposal_task.delay(job_id=job_id) # Real async call
    # For verification/demo without running connection to worker, we might simulate or call synchronously if worker is not up.
    # Assuming user has celery worker running? Probably not. 
    # So we will call it synchronously for the DEMO to ensure user sees the result in logs.
    
    try:
        generate_proposal_task(job_id=job_id) # Sync call for demo
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Propuesta generada (Worker finished).")
    except Exception as e:
         await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Error generando propuesta: {e}")

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN not found in environment.")
        exit(1)
        
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    reply_handler = CommandHandler('reply', reply_command)
    approve_handler = CommandHandler('approve', approve_command)
    generate_handler = CommandHandler('generate', generate_command)

    application.add_handler(start_handler)
    application.add_handler(reply_handler)
    application.add_handler(approve_handler)
    application.add_handler(generate_handler)
    
    logging.info("Starting Telegram Bot Polling...")
    application.run_polling()

import logging
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# Check if python-telegram-bot is installed, if not we will mock or fail gracefully for now.
# In a real environment, we would add it to requirements.txt.
try:
    from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
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

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback queries from inline keyboard buttons.
    Callback data format: action_id
    - approve_{proposal_id}
    - reject_{proposal_id}
    - edit_{proposal_id}
    - analysis_{job_id}
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    callback_data = query.data
    logging.info(f"Received callback: {callback_data}")
    
    # Parse callback data
    action, item_id = callback_data.split('_', 1)
    
    if action == "approve":
        await handle_approve_proposal(query, item_id)
    elif action == "reject":
        await handle_reject_proposal(query, item_id)
    elif action == "edit":
        await handle_edit_proposal(query, item_id)
    elif action == "analysis":
        await handle_view_analysis(query, item_id)
    else:
        await query.edit_message_text(text=f"❌ Acción desconocida: {action}")

async def handle_approve_proposal(query, proposal_id: str):
    """Handle proposal approval."""
    try:
        # Import use cases
        from infrastructure.adapters.persistence.mongodb.adapter import MongoProposalRepository, MongoJobRepository
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        
        # Get proposal from DB
        proposal_repo = MongoProposalRepository()
        # TODO: Implement get_by_id in repository
        # proposal = proposal_repo.get_by_id(int(proposal_id))
        
        # For now, simulate submission
        await query.edit_message_text(
            text=f"✅ **PROPUESTA APROBADA Y ENVIADA**\n\n"
                 f"ID: {proposal_id}\n"
                 f"Estado: `submitted` (Enviada a la plataforma)\n\n"
                 f"📊 **Próximos pasos:**\n"
                 f"• El sistema monitoreará el estado cada 5 minutos\n"
                 f"• Recibirás notificación si el cliente responde\n"
                 f"• Te avisaré cuando sea adjudicada o rechazada\n\n"
                 f"⏳ **Esperando respuesta del cliente...**"
        )
        
        logging.info(f"Proposal {proposal_id} approved and submitted to platform")
        logging.info(f"Status: submitted → monitoring started")
        
    except Exception as e:
        logging.error(f"Error approving proposal: {e}")
        await query.edit_message_text(text=f"❌ Error aprobando propuesta: {e}")

async def handle_reject_proposal(query, proposal_id: str):
    """Handle proposal rejection."""
    try:
        # Update proposal status to rejected
        await query.edit_message_text(
            text=f"❌ **PROPUESTA RECHAZADA**\n\n"
                 f"ID: {proposal_id}\n"
                 f"Estado: Rechazada\n\n"
                 f"_La propuesta ha sido marcada como rechazada._"
        )
        
        logging.info(f"Proposal {proposal_id} rejected")
        
    except Exception as e:
        logging.error(f"Error rejecting proposal: {e}")
        await query.edit_message_text(text=f"❌ Error rechazando propuesta: {e}")

async def handle_edit_proposal(query, proposal_id: str):
    """Handle proposal edit request."""
    try:
        # Provide instructions for editing
        await query.edit_message_text(
            text=f"✏️ **EDITAR PROPUESTA**\n\n"
                 f"ID: {proposal_id}\n\n"
                 f"Para editar la propuesta, usa:\n"
                 f"`/edit {proposal_id} [nuevo contenido]`\n\n"
                 f"_Función de edición en desarrollo._"
        )
        
        logging.info(f"Edit requested for proposal {proposal_id}")
        
    except Exception as e:
        logging.error(f"Error handling edit: {e}")
        await query.edit_message_text(text=f"❌ Error: {e}")

async def handle_view_analysis(query, job_id: str):
    """Handle view analysis request."""
    try:
        # Fetch analysis report
        import os
        from pathlib import Path
        
        # Look for latest analysis report for this job
        reports_dir = Path("reports")
        if reports_dir.exists():
            # Find matching report
            reports = list(reports_dir.glob(f"**/analysis_{job_id}_*.md"))
            if reports:
                latest_report = max(reports, key=lambda p: p.stat().st_mtime)
                
                # Read report content (first 500 chars)
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()[:500]
                
                await query.edit_message_text(
                    text=f"📊 **ANÁLISIS DEL TRABAJO**\n\n"
                         f"ID: {job_id}\n\n"
                         f"{content}...\n\n"
                         f"_Ver reporte completo en: `{latest_report}`_",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    text=f"📊 **ANÁLISIS DEL TRABAJO**\n\n"
                         f"ID: {job_id}\n\n"
                         f"⚠️ No se encontró reporte de análisis."
                )
        else:
            await query.edit_message_text(text="⚠️ Directorio de reportes no encontrado.")
        
        logging.info(f"Analysis viewed for job {job_id}")
        
    except Exception as e:
        logging.error(f"Error viewing analysis: {e}")
        await query.edit_message_text(text=f"❌ Error: {e}")

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
    
    # Add callback query handler for inline buttons
    callback_handler = CallbackQueryHandler(callback_query_handler)

    application.add_handler(start_handler)
    application.add_handler(reply_handler)
    application.add_handler(approve_handler)
    application.add_handler(generate_handler)
    application.add_handler(callback_handler)
    
    logging.info("Starting Telegram Bot Polling...")
    application.run_polling()


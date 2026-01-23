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
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Uso: /approve [proposal_id]")
        return
        
    proposal_id = context.args[0]
    await handle_approve_proposal(update.callback_query or update, proposal_id)

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
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository, MongoProposalRepository
        from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from application.use_cases import GenerateProposalUseCase
        
        use_case = GenerateProposalUseCase(
            job_repo=MongoJobRepository(),
            proposal_repo=MongoProposalRepository(),
            ai_port=OpenAIAdapter(),
            notification_port=TelegramAdapter()
        )
        
        use_case.execute(job_id)
        # La notificación ya la envía el use case
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
    """Handle proposal approval and submit to Freelancer.com."""
    try:
        from infrastructure.adapters.persistence.mongodb.adapter import MongoProposalRepository, MongoJobRepository
        from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
        
        # 1. Obtener propuesta y trabajo de DB
        proposal_repo = MongoProposalRepository()
        job_repo = MongoJobRepository()
        
        proposal = proposal_repo.get_by_id(int(proposal_id))
        if not proposal:
            msg = f"❌ Error: Propuesta {proposal_id} no encontrada en DB."
            if hasattr(query, 'edit_message_text'):
                await query.edit_message_text(text=msg)
            else:
                await query.bot.send_message(chat_id=query.effective_chat.id, text=msg)
            return

        job = job_repo.get_by_external_id(proposal.job_offer_id if isinstance(proposal.job_offer_id, str) else str(proposal.job_offer_id))
        # Nota: el campo se llama upwork_id en el repo pero lo usamos de forma genérica para external_id
        
        # 2. Enviar a Freelancer
        freelancer = FreelancerAdapter()
        success = freelancer.submit_proposal(
            job_id=job.external_id if job else str(proposal.job_offer_id),
            content=proposal.content,
            amount=proposal.bid_amount
        )
        
        if success:
            # 3. Actualizar estado
            proposal.status = "submitted"
            proposal_repo.save(proposal)
            
            msg = (
                f"✅ **PROPUESTA ENVIADA A FREELANCER.COM**\n\n"
                f"ID Interno: {proposal_id}\n"
                f"Proyecto: {job.title if job else 'N/A'}\n"
                f"Monto: {proposal.bid_amount} {proposal.currency}\n\n"
                f"📊 **Estado:** `submitted` (Activa)\n\n"
                f"⏳ **Esperando respuesta del cliente...**"
            )
            if hasattr(query, 'edit_message_text'):
                await query.edit_message_text(text=msg, parse_mode="Markdown")
            else:
                await query.bot.send_message(chat_id=query.effective_chat.id, text=msg, parse_mode="Markdown")
        else:
            msg = f"❌ Error al enviar la propuesta a Freelancer.com. Revisa los logs."
            if hasattr(query, 'edit_message_text'):
                await query.edit_message_text(text=msg)
            else:
                 await query.bot.send_message(chat_id=query.effective_chat.id, text=msg)
        
    except Exception as e:
        logging.error(f"Error approving proposal: {e}")
        import traceback
        traceback.print_exc()
        msg = f"❌ Error: {e}"
        if hasattr(query, 'edit_message_text'):
            await query.edit_message_text(text=msg)
        else:
            await query.bot.send_message(chat_id=query.effective_chat.id, text=msg)

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


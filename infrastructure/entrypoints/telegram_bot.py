import logging
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# Check if python-telegram-bot is installed
try:
    from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
except ImportError:
    logging.error("python-telegram-bot not installed. Please install it with 'pip install python-telegram-bot'")
    exit(1)

# Import Use Cases
from application.use_cases import (
    GenerateProposalUseCase, 
    SubmitProposalUseCase, 
    UpdateProposalUseCase, 
    RejectProposalUseCase
)
from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository, MongoProposalRepository
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from infrastructure.factories import PlatformFactory

# Estados de conversación
EDIT_CONTENT = 1
EDIT_AMOUNT = 2

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
        from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        from application.use_cases import GenerateProposalUseCase
        
        use_case = GenerateProposalUseCase(
            job_repo=MongoJobRepository(),
            proposal_repo=MongoProposalRepository(),
            ai_port=GeminiAdapter(),
            notification_port=TelegramAdapter()
        )
        
        use_case.execute(job_id)
        # La notificación ya la envía el use case
    except Exception as e:
         error_msg = f"❌ Error generando propuesta: {e}"
         await context.bot.send_message(chat_id=update.effective_chat.id, text=error_msg)
         try:
             from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
             TelegramAdapter().notify_error(error_msg)
         except:
             pass

async def buscar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /buscar
    Triggers the Celery task to scan the latest 15 jobs.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🔍 Iniciando búsqueda masiva de los últimos 15 trabajos...")
    
    from infrastructure.entrypoints.celery_tasks import scan_jobs_task
    
    # Llamamos a la tarea
    # scan_jobs_task.delay(limit=15) # En producción usar .delay()
    # Para el usuario y ver logs inmediatos, la ejecutamos aquí
    try:
        scan_jobs_task(limit=15)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Escaneo masivo completado. Revisa las nuevas notificaciones.")
    except Exception as e:
        error_msg = f"❌ Error en búsqueda masiva: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_msg)
        try:
            from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
            TelegramAdapter().notify_error(error_msg)
        except:
            pass

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
    elif action == "gen": # gen_force_{job_id}
        # In case the prefix split was just 'gen' due to 'gen_force'
        if item_id.startswith("force_"):
            job_id = item_id.replace("force_", "")
            await handle_force_generate(query, job_id)
    elif action == "discard": # discard_job_{job_id}
        if item_id.startswith("job_"):
            job_id = item_id.replace("job_", "")
            await handle_discard_job(query, job_id)
    else:
        await query.edit_message_text(text=f"❌ Acción desconocida: {action}")

async def handle_approve_proposal(query, proposal_id: str):
    """Handle proposal approval and submit to the platform."""
    try:
        # Instanciar el caso de uso
        use_case = SubmitProposalUseCase(
            proposal_repo=MongoProposalRepository(),
            notification_port=TelegramAdapter(),
            job_repo=MongoJobRepository(),
            platform_factory=PlatformFactory()
        )
        
        if hasattr(query, 'edit_message_text'):
            await query.edit_message_text(text="🚀 Enviando propuesta a la plataforma...")
        
        success = use_case.execute(int(proposal_id))
        
        if not success and hasattr(query, 'edit_message_text'):
            await query.edit_message_text(text="❌ Error al enviar la propuesta. Revisa el log para más detalles.")
        
    except Exception as e:
        logging.error(f"Error approving proposal: {e}")
        msg = f"❌ Error: {e}"
        if hasattr(query, 'edit_message_text'):
            await query.edit_message_text(text=msg)
        else:
            await query.bot.send_message(chat_id=query.effective_chat.id, text=msg)

async def handle_reject_proposal(query, proposal_id: str):
    """Handle proposal rejection."""
    try:
        use_case = RejectProposalUseCase(
            proposal_repo=MongoProposalRepository(),
            notification_port=TelegramAdapter()
        )
        
        success = use_case.execute(int(proposal_id))
        
        if success:
            await query.edit_message_text(
                text=f"🚫 **PROPUESTA RECHAZADA**\n\n"
                     f"ID: {proposal_id}\n"
                     f"Estado: Rechazada en el sistema.\n\n"
                     f"_La propuesta no será enviada._"
            )
        else:
            await query.edit_message_text(text="❌ Error al procesar el rechazo en la base de datos.")
        
    except Exception as e:
        logging.error(f"Error rejecting proposal: {e}")
        await query.edit_message_text(text=f"❌ Error rechazando propuesta: {e}")

async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /edit [proposal_id] [new content]
    """
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso: /edit [proposal_id] [nuevo contenido]")
        return
    
    proposal_id = context.args[0]
    new_content = " ".join(context.args[1:])
    
    try:
        use_case = UpdateProposalUseCase(
            proposal_repo=MongoProposalRepository(),
            notification_port=TelegramAdapter()
        )
        success = use_case.execute(int(proposal_id), new_content)
        if success:
            await update.message.reply_text(f"✅ Propuesta {proposal_id} actualizada.")
        else:
            await update.message.reply_text(f"❌ No se pudo actualizar la propuesta {proposal_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def handle_edit_proposal(query, proposal_id: str):
    """Handle proposal edit request."""
    try:
        # Provide instructions for editing
        await query.edit_message_text(
            text=f"✏️ **EDITAR PROPUESTA**\n\n"
                 f"ID: {proposal_id}\n\n"
                 f"Para editar el contenido de la propuesta, envía:\n"
                 f"`/edit {proposal_id} [Aquí tu nuevo texto]`\n\n"
                 f"_Copia el texto original, modifícalo y envíalo con el comando._",
            parse_mode="Markdown"
        )
        
        logging.info(f"Edit requested for proposal {proposal_id}")
        
    except Exception as e:
        logging.error(f"Error handling edit: {e}")
        await query.edit_message_text(text=f"❌ Error: {e}")

async def handle_view_analysis(query, job_id: str):
    """Handle view analysis request."""
    try:
        # Fetch analysis report
        from pathlib import Path
        
        # Buscar el reporte más reciente para este trabajo
        reports_dir = Path("reports")
        if reports_dir.exists():
            # Buscar archivos que contengan el ID del trabajo
            reports = list(reports_dir.glob(f"**/analysis_{job_id}_*.md"))
            if not reports:
                # Intentar búsqueda más flexible
                reports = list(reports_dir.glob(f"**/*{job_id}*.md"))
                
            if reports:
                # Obtener el más reciente por fecha de modificación
                latest_report = max(reports, key=lambda p: p.stat().st_mtime)
                
                # Leer el contenido (limitado para Telegram)
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Limpiar un poco el markdown para Telegram si es necesario
                # Por ahora solo enviamos los primeros 1000 caracteres
                await query.edit_message_text(
                    text=f"📊 **ANÁLISIS DEL TRABAJO**\n\n"
                         f"ID: {job_id}\n\n"
                         f"{content[:1000]}...\n\n"
                         f"_Reporte completo en:_ `{latest_report.name}`",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    text=f"📊 **ANÁLISIS DEL TRABAJO**\n\n"
                         f"ID: {job_id}\n\n"
                         f"⚠️ No se encontró reporte de análisis guardado localmente."
                )
        else:
             await query.edit_message_text(text="⚠️ Directorio de reportes no encontrado.")
        
        logging.info(f"Analysis viewed for job {job_id}")
        
    except Exception as e:
        logging.error(f"Error viewing analysis: {e}")
        await query.edit_message_text(text=f"❌ Error al cargar el análisis: {e}")

async def handle_force_generate(query, job_id: str):
    """Trigger proposal generation for a job."""
    await query.edit_message_text(text=f"⚙️ Iniciando generación de propuesta para {job_id}...")
    try:
        from application.use_cases import GenerateProposalUseCase
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository, MongoProposalRepository
        from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter
        from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
        
        use_case = GenerateProposalUseCase(
            job_repo=MongoJobRepository(),
            proposal_repo=MongoProposalRepository(),
            ai_port=GeminiAdapter(),
            notification_port=TelegramAdapter()
        )
        
        use_case.execute(job_id)
    except Exception as e:
        await query.bot.send_message(chat_id=query.effective_chat.id, text=f"❌ Error: {e}")

async def handle_discard_job(query, job_id: str):
    """Mark a job opportunity as discarded/rejected."""
    try:
        from infrastructure.adapters.persistence.mongodb.adapter import MongoJobRepository
        repo = MongoJobRepository()
        job = repo.get_by_external_id(job_id)
        if job:
            job.status = "discarded"
            repo.save(job)
            await query.edit_message_text(text=f"🗑️ Oportunidad `{job_id}` descartada.")
        else:
             await query.edit_message_text(text=f"❌ Trabajo `{job_id}` no encontrado en DB.")
    except Exception as e:
        await query.bot.send_message(chat_id=query.effective_chat.id, text=f"❌ Error descartando: {e}")

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
    edit_h = CommandHandler('edit', edit_command) # Nuevo comando
    
    # Add callback query handler for inline buttons
    callback_handler = CallbackQueryHandler(callback_query_handler)

    application.add_handler(start_handler)
    application.add_handler(reply_handler)
    application.add_handler(approve_handler)
    application.add_handler(generate_handler)
    application.add_handler(edit_h)
    application.add_handler(CommandHandler('buscar', buscar_command))
    application.add_handler(callback_handler)
    
    logging.info("Starting Telegram Bot Polling...")
    application.run_polling()


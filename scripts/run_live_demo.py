"""
Demo Interactivo: Bot + Propuesta + Espera Respuesta

Este script:
1. Inicia el bot de Telegram
2. Analiza un trabajo
3. Genera y envía propuesta a Telegram
4. Espera que el usuario haga clic en un botón
5. Procesa la respuesta
6. NO se cierra hasta recibir interacción
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Telegram imports
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
except ImportError:
    print("ERROR: python-telegram-bot no instalado")
    print("Instala con: pip install python-telegram-bot")
    sys.exit(1)

# Project imports
from infrastructure.adapters.analyzer.gemini.adapter import GeminiAdapter
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from infrastructure.utils.report_generator import MarkdownReportGenerator
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

# Variable global para rastrear si se recibió respuesta
response_received = False
response_action = None

async def send_test_proposal(application):
    """Envía una propuesta de prueba a Telegram."""
    logger.info("=" * 70)
    logger.info("INICIANDO DEMO: Análisis → Propuesta → Telegram")
    logger.info("=" * 70)
    
    # Crear trabajo de prueba
    job = JobOffer(
        external_id=f"live_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        title="Senior Full Stack Developer - React & Node.js",
        description="""
        We need an experienced full-stack developer for a 6-week project.
        
        Tech Stack:
        - Frontend: React.js, TypeScript, TailwindCSS
        - Backend: Node.js, Express, MongoDB
        - DevOps: Docker, AWS deployment
        
        Deliverables:
        - Complete web application
        - Admin dashboard
        - REST API with authentication
        - Deployment to AWS
        
        Budget: $4000-6000
        Timeline: 6 weeks
        """.strip(),
        budget="4000-6000 USD",
        min_amount=4000.0,
        currency="USD",
        status="pending",
        category="Full Stack Development"
    )
    
    logger.info(f"Trabajo creado: {job.title}")
    
    # Analizar con Gemini
    logger.info("Analizando con Gemini...")
    try:
        gemini = GeminiAdapter()
        analysis = gemini.analyze_job(job)
        score = analysis.get('score', 0)
        logger.info(f"Análisis completado - Score: {score}/100")
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        return
    
    # Generar reporte
    logger.info("Generando reporte markdown...")
    try:
        report_gen = MarkdownReportGenerator(output_dir="reports/live_demo")
        report_path = report_gen.generate_job_analysis_report(job, analysis)
        logger.info(f"Reporte: {report_path}")
    except Exception as e:
        logger.warning(f"Error generando reporte: {e}")
    
    # Generar propuesta
    logger.info("Generando propuesta...")
    try:
        proposal_content = gemini.generate_proposal_content(job)
        logger.info(f"Propuesta generada ({len(proposal_content)} chars)")
    except Exception as e:
        logger.error(f"Error generando propuesta: {e}")
        return
    
    # Enviar a Telegram
    logger.info("Enviando a Telegram...")
    try:
        telegram = TelegramAdapter()
        proposal_id = int(datetime.now().timestamp())
        
        success = telegram.send_proposal_for_validation(
            job_title=job.title,
            proposal_content=proposal_content,
            proposal_id=proposal_id,
            job_id=job.external_id,
            analysis_score=score
        )
        
        if success:
            logger.info("=" * 70)
            logger.info("PROPUESTA ENVIADA A TELEGRAM")
            logger.info("=" * 70)
            logger.info("")
            logger.info("📱 REVISA TU TELEGRAM Y HAZ CLIC EN UN BOTÓN:")
            logger.info("   • ✅ Aprobar y Enviar")
            logger.info("   • ❌ Rechazar")
            logger.info("   • ✏️ Editar")
            logger.info("   • 📊 Ver Análisis")
            logger.info("")
            logger.info("⏳ ESPERANDO TU RESPUESTA...")
            logger.info("   (El bot seguirá corriendo hasta que hagas clic)")
            logger.info("")
        else:
            logger.error("Error enviando a Telegram")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de los botones."""
    global response_received, response_action
    
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    action, item_id = callback_data.split('_', 1)
    
    logger.info("=" * 70)
    logger.info(f"🎉 RESPUESTA RECIBIDA: {action.upper()}")
    logger.info("=" * 70)
    
    response_received = True
    response_action = action
    
    if action == "approve":
        await query.edit_message_text(
            text=f"✅ **PROPUESTA APROBADA**\n\n"
                 f"ID: {item_id}\n"
                 f"Estado: Aprobada y lista para enviar\n\n"
                 f"_En producción, esta propuesta se enviaría automáticamente a la plataforma._"
        )
        logger.info(f"✅ Propuesta {item_id} APROBADA")
        
    elif action == "reject":
        await query.edit_message_text(
            text=f"❌ **PROPUESTA RECHAZADA**\n\n"
                 f"ID: {item_id}\n"
                 f"Estado: Rechazada\n\n"
                 f"_La propuesta ha sido descartada._"
        )
        logger.info(f"❌ Propuesta {item_id} RECHAZADA")
        
    elif action == "edit":
        await query.edit_message_text(
            text=f"✏️ **EDITAR PROPUESTA**\n\n"
                 f"ID: {item_id}\n\n"
                 f"Para editar, usa:\n"
                 f"`/edit {item_id} [nuevo contenido]`\n\n"
                 f"_Función de edición en desarrollo._"
        )
        logger.info(f"✏️ Edición solicitada para propuesta {item_id}")
        
    elif action == "analysis":
        await query.edit_message_text(
            text=f"📊 **ANÁLISIS DEL TRABAJO**\n\n"
                 f"ID: {item_id}\n\n"
                 f"El análisis completo está disponible en el reporte markdown.\n"
                 f"Revisa la carpeta `reports/live_demo/`"
        )
        logger.info(f"📊 Análisis solicitado para {item_id}")
    
    logger.info("")
    logger.info("✅ Demo completado exitosamente")
    logger.info("Presiona Ctrl+C para detener el bot")
    logger.info("")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start."""
    await update.message.reply_text(
        "🤖 Bot de Demo Activo\n\n"
        "Esperando que hagas clic en los botones de la propuesta..."
    )

async def main():
    """Función principal."""
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no encontrado en .env")
        return
    
    # Crear aplicación
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Agregar handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Iniciar bot
    logger.info("🚀 Iniciando bot de Telegram...")
    await application.initialize()
    await application.start()
    
    # Enviar propuesta de prueba
    await send_test_proposal(application)
    
    # Iniciar polling
    logger.info("👂 Bot escuchando callbacks...")
    await application.updater.start_polling()
    
    # Esperar indefinidamente hasta Ctrl+C
    try:
        while True:
            await asyncio.sleep(1)
            if response_received:
                # Dar tiempo para que se procese el mensaje
                await asyncio.sleep(2)
                logger.info("\n🎯 Respuesta procesada. Puedes cerrar con Ctrl+C o esperar más interacciones.")
    except KeyboardInterrupt:
        logger.info("\n\n👋 Deteniendo bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("✅ Bot detenido correctamente")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo finalizado")

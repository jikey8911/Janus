"""
Demo End-to-End: Análisis → Propuesta → Telegram → Espera Aprobación

Este script demuestra el flujo completo:
1. Analiza un trabajo con Gemini
2. Genera propuesta
3. Envía a Telegram con botones inline
4. Espera respuesta del usuario (simulado)
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from dotenv import load_dotenv
from infrastructure.adapters.analyzer.gemini.adapter import GeminiAdapter
from infrastructure.adapters.notification.telegram.adapter import TelegramAdapter
from infrastructure.utils.report_generator import MarkdownReportGenerator
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
load_dotenv()

def main():
    print("=" * 70)
    print("🚀 DEMO END-TO-END: Análisis → Propuesta → Telegram")
    print("=" * 70)
    
    # ========== PASO 1: Crear trabajo de prueba ==========
    print("\n[PASO 1/5] Creando trabajo de prueba...")
    job = JobOffer(
        external_id="demo_e2e_001",
        title="Python Backend Developer - FastAPI & PostgreSQL",
        description="""
        We're looking for an experienced Python developer to build a REST API.
        
        Requirements:
        - 3+ years Python experience
        - FastAPI framework
        - PostgreSQL database design
        - Docker containerization
        - Unit testing with pytest
        
        Deliverables:
        - Complete REST API with CRUD operations
        - Database migrations
        - API documentation (Swagger)
        - Docker compose setup
        
        Budget: $2000-3500
        Timeline: 3 weeks
        """.strip(),
        budget="2000-3500 USD",
        min_amount=2000.0,
        currency="USD",
        status="pending",
        category="Backend Development"
    )
    print(f"✅ Trabajo creado: {job.title}")
    print(f"   ID: {job.external_id}")
    print(f"   Presupuesto: {job.budget}")
    
    # ========== PASO 2: Analizar con Gemini ==========
    print("\n[PASO 2/5] Analizando trabajo con Gemini AI...")
    try:
        gemini = GeminiAdapter()
        if not gemini.model:
            print("❌ ERROR: Gemini no inicializado")
            return
        
        analysis = gemini.analyze_job(job)
        score = analysis.get('score', 0)
        viability = analysis.get('viability_analysis', 'N/A')
        
        print(f"✅ Análisis completado:")
        print(f"   Score: {score}/100")
        print(f"   Viabilidad: {viability[:100]}...")
        
    except Exception as e:
        print(f"❌ ERROR en análisis: {e}")
        return
    
    # ========== PASO 3: Generar reporte markdown ==========
    print("\n[PASO 3/5] Generando reporte markdown...")
    try:
        report_gen = MarkdownReportGenerator(output_dir="reports/demo")
        report_path = report_gen.generate_job_analysis_report(job, analysis)
        print(f"✅ Reporte generado: {report_path}")
    except Exception as e:
        print(f"⚠️ Error generando reporte: {e}")
    
    # ========== PASO 4: Generar propuesta ==========
    print("\n[PASO 4/5] Generando propuesta con Gemini...")
    try:
        proposal_content = gemini.generate_proposal_content(job)
        print(f"✅ Propuesta generada ({len(proposal_content)} caracteres)")
        print(f"\n--- PREVIEW DE PROPUESTA ---")
        print(proposal_content[:300] + "...")
        print(f"--- FIN PREVIEW ---\n")
    except Exception as e:
        print(f"❌ ERROR generando propuesta: {e}")
        return
    
    # ========== PASO 5: Enviar a Telegram ==========
    print("\n[PASO 5/5] Enviando propuesta a Telegram con botones...")
    try:
        telegram = TelegramAdapter()
        
        # Simular ID de propuesta guardada en DB
        proposal_id = 99999
        
        success = telegram.send_proposal_for_validation(
            job_title=job.title,
            proposal_content=proposal_content,
            proposal_id=proposal_id,
            job_id=job.external_id,
            analysis_score=score
        )
        
        if success:
            print(f"✅ Propuesta enviada a Telegram exitosamente")
            print(f"\n📱 REVISA TU TELEGRAM:")
            print(f"   - Verás la propuesta completa")
            print(f"   - Score del análisis: {score}/100")
            print(f"   - 4 botones de acción:")
            print(f"     • ✅ Aprobar y Enviar")
            print(f"     • ❌ Rechazar")
            print(f"     • ✏️ Editar")
            print(f"     • 📊 Ver Análisis")
            print(f"\n⏳ ESPERANDO RESPUESTA DEL USUARIO...")
            print(f"   (El bot está escuchando los clicks en los botones)")
            print(f"\n💡 Para procesar la respuesta:")
            print(f"   1. Asegúrate de que el bot esté corriendo:")
            print(f"      python infrastructure/entrypoints/telegram_bot.py")
            print(f"   2. Haz clic en cualquier botón en Telegram")
            print(f"   3. El handler procesará la acción automáticamente")
        else:
            print(f"❌ Error enviando a Telegram")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADO - Flujo End-to-End Ejecutado")
    print("=" * 70)
    print(f"\n📊 Resumen:")
    print(f"   • Trabajo analizado: {job.title}")
    print(f"   • Score: {score}/100")
    print(f"   • Propuesta generada: {len(proposal_content)} caracteres")
    print(f"   • Reporte: {report_path if 'report_path' in locals() else 'N/A'}")
    print(f"   • Enviado a Telegram: ✅")
    print(f"\n🎯 Próximo paso: Haz clic en un botón en Telegram para probar los handlers")
    print()

if __name__ == "__main__":
    main()

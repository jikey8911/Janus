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
from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter
from infrastructure.adapters.analyzer.openai.adapter import OpenAIAdapter
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
    print("🚀 LIVE END-TO-END: Freelancer → OpenAI → Telegram")
    print("=" * 70)
    
    # ========== PASO 1: Obtener trabajo real de Freelancer ==========
    print("\n[PASO 1/5] Obteniendo trabajo real de Freelancer...")
    try:
        freelancer = FreelancerAdapter()
        all_jobs = freelancer.search_jobs()
        
        if not all_jobs:
            print("❌ ERROR: No se encontraron trabajos en Freelancer.")
            return
            
        job = all_jobs[0]
        print(f"✅ Trabajo capturado: {job.title}")
        print(f"   ID: {job.external_id}")
        print(f"   Presupuesto: {job.budget} {job.currency}")
    except Exception as e:
        print(f"❌ ERROR conectando a Freelancer: {e}")
        return
    
    # ========== PASO 2: Analizar con OpenAI ==========
    print("\n[PASO 2/5] Analizando trabajo con OpenAI...")
    try:
        openai_analyzer = OpenAIAdapter()
        if not openai_analyzer.client:
            print("❌ ERROR: OpenAI no inicializado")
            return
        
        analysis = openai_analyzer.analyze_job(job)
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
    print("\n[PASO 4/5] Generando propuesta con OpenAI...")
    try:
        proposal_content = openai_analyzer.generate_proposal_content(job)
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

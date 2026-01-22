"""
Script de verificación para HU 5.1: Diagnóstico completo
Prueba la integración de GeminiAdapter con generación de reportes markdown.
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from dotenv import load_dotenv
from infrastructure.adapters.analyzer.gemini.adapter import GeminiAdapter
from infrastructure.utils.report_generator import MarkdownReportGenerator
from domain.entities import JobOffer

# Configurar logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

def main():
    print("=" * 60)
    print("HU 5.1 - Verificación Completa: Diagnóstico + Reporte")
    print("=" * 60)
    
    # 1. Verificar GeminiAdapter
    print("\n[1/3] Inicializando GeminiAdapter...")
    try:
        adapter = GeminiAdapter()
        if not adapter.model:
            print("❌ ERROR: Modelo Gemini no inicializado")
            return
        print("✅ GeminiAdapter inicializado correctamente")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return
    
    # 2. Crear oferta de prueba
    print("\n[2/3] Creando oferta de prueba...")
    job = JobOffer(
        external_id="test_hu51_001",
        title="Full Stack Developer - React & Python API",
        description="""
        We need an experienced full-stack developer to build a modern web application.
        
        Requirements:
        - React.js for frontend (TypeScript preferred)
        - Python FastAPI for backend
        - PostgreSQL database
        - Docker deployment
        - CI/CD pipeline setup
        
        Budget: $3000-5000
        Timeline: 4-6 weeks
        """,
        budget="3000-5000 USD",
        min_amount=3000.0,
        currency="USD",
        status="pending",
        category="Web Development"
    )
    print(f"✅ Oferta creada: {job.title}")
    
    # 3. Analizar con Gemini
    print("\n[3/3] Analizando oferta con Gemini...")
    try:
        analysis = adapter.analyze_job(job)
        print(f"\n📊 Resultado del Análisis:")
        print(f"   Score: {analysis.get('score', 0)}/100")
        print(f"   Viabilidad: {analysis.get('viability_analysis', 'N/A')}")
        print(f"   Riesgos: {len(analysis.get('key_risks', []))} identificados")
        print(f"   Stack: {', '.join(analysis.get('recommended_stack', []))}")
    except Exception as e:
        print(f"❌ ERROR en análisis: {e}")
        return
    
    # 4. Generar reporte markdown
    print("\n[4/4] Generando reporte markdown...")
    try:
        report_gen = MarkdownReportGenerator(output_dir="reports/test")
        report_path = report_gen.generate_job_analysis_report(job, analysis)
        print(f"✅ Reporte generado: {report_path}")
        
        # Mostrar preview del reporte
        with open(report_path, 'r', encoding='utf-8') as f:
            preview = f.read()[:500]
        print(f"\n📄 Preview del reporte:\n{preview}...")
        
    except Exception as e:
        print(f"❌ ERROR generando reporte: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ HU 5.1 VERIFICACIÓN COMPLETA - TODOS LOS TESTS PASARON")
    print("=" * 60)

if __name__ == "__main__":
    main()

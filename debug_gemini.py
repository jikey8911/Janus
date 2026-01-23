
import os
import logging
import json
from dotenv import load_dotenv
from domain.entities import JobOffer
from infrastructure.adapters.analyzer.gemini.gemini_clean import GeminiAdapter

# Configurar logging para ver TODO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_gemini_analysis():
    load_dotenv()
    print("--- INICIANDO TEST DE ANÁLISIS GEMINI ---")
    
    # 1. Verificar API KEY
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY no encontrada en .env")
        return
    else:
        print(f"✅ API KEY detectada (comienza con {api_key[:5]}...)")

    # 2. Instanciar adaptador
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        print("✅ Cliente google-genai instanciado.")
        
        print("🔄 Test directo de generación...")
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Dime hola en español'
        )
        print(f"✅ Respuesta directa: {response.text}")
             
    except Exception as e:
        print(f"❌ ERROR en test directo: {e}")
        return

    # 3. Crear Job de prueba
    test_job = JobOffer(
        external_id="test_123",
        title="Python Web Scraper for E-commerce",
        description="I need a Python expert to build a web scraper for Amazon and eBay. Must use BeautifulSoup or Selenium.",
        budget="100-500 USD",
        min_amount=100.0,
        currency="USD"
    )
    print("✅ Job de prueba creado.")

    # 4. Ejecutar análisis
    print("🔄 Ejecutando analyze_job...")
    try:
        analysis = adapter.analyze_job(test_job)
        print("--- RESULTADO DEL ANÁLISIS ---")
        print(json.dumps(analysis, indent=2))
        
        if "score" in analysis:
            print(f"✅ ÉXITO: Score recibido: {analysis['score']}")
        else:
            print("⚠️ ADVERTENCIA: No se recibió score en la respuesta.")
            
        if "viability" in analysis or "viability_analysis" in analysis:
             v = analysis.get("viability") or analysis.get("viability_analysis")
             print(f"✅ ÉXITO: Análisis de viabilidad recibido: {v[:50]}...")
        else:
            print("⚠️ ADVERTENCIA: No se recibió texto de viabilidad.")

    except Exception as e:
        print(f"❌ ERROR durante la ejecución del análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_analysis()

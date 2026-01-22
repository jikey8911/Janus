import os
import logging
from datetime import datetime
from typing import Dict, Any
from domain.entities import JobOffer

class MarkdownReportGenerator:
    """Generador de reportes de análisis en formato Markdown."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Args:
            output_dir: Directorio donde se guardarán los reportes
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_job_analysis_report(
        self, 
        job: JobOffer, 
        analysis: Dict[str, Any]
    ) -> str:
        """
        Genera un reporte markdown del análisis de una oferta.
        
        Args:
            job: Oferta de trabajo analizada
            analysis: Resultado del análisis de IA
            
        Returns:
            Ruta del archivo generado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{job.external_id}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Construir contenido del reporte
        content = self._build_report_content(job, analysis)
        
        # Guardar archivo
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Reporte generado: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error generando reporte: {e}")
            raise
    
    def _build_report_content(self, job: JobOffer, analysis: Dict[str, Any]) -> str:
        """Construye el contenido markdown del reporte."""
        
        score = analysis.get('score', 0)
        viability = analysis.get('viability_analysis', 'N/A')
        risks = analysis.get('key_risks', [])
        stack = analysis.get('recommended_stack', [])
        research = analysis.get('research_topics', [])
        
        # Determinar emoji según score
        if score >= 80:
            emoji = "🟢"
            verdict = "ALTA VIABILIDAD"
        elif score >= 60:
            emoji = "🟡"
            verdict = "VIABILIDAD MEDIA"
        else:
            emoji = "🔴"
            verdict = "BAJA VIABILIDAD"
        
        content = f"""# Análisis de Oferta: {job.title}

{emoji} **{verdict}** - Score: {score}/100

---

## 📋 Información de la Oferta

- **ID Externo:** `{job.external_id}`
- **Título:** {job.title}
- **Presupuesto:** {job.budget}
- **Categoría:** {job.category or 'N/A'}
- **Estado:** {job.status}

---

## 🔍 Descripción

{job.description}

---

## 🧠 Análisis de Viabilidad

{viability}

---

## ⚠️ Riesgos Identificados

"""
        if risks:
            for risk in risks:
                content += f"- {risk}\n"
        else:
            content += "*No se identificaron riesgos específicos.*\n"
        
        content += f"""
---

## 🛠️ Stack Tecnológico Recomendado

"""
        if stack:
            for tech in stack:
                content += f"- `{tech}`\n"
        else:
            content += "*No se especificó stack.*\n"
        
        content += f"""
---

## 📚 Temas de Investigación

"""
        if research:
            for topic in research:
                content += f"- {topic}\n"
        else:
            content += "*No se requiere investigación adicional.*\n"
        
        content += f"""
---

*Reporte generado automáticamente por Janus AI*  
*Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return content

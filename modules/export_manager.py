"""
Export Utilities Module
Handles data export functionality (PDF, JSON, etc.)
"""

import io
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import logging

logger = logging.getLogger(__name__)


class ExportManager:
    def __init__(self):
        pass
    
    def export_to_pdf(self, entries):
        """Export entries to PDF format"""
        try:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setTitle("JARVIS Diary Export")
            
            y_position = 750
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, "JARVIS AI Diary Export")
            y_position -= 30
            
            p.setFont("Helvetica", 12)
            for entry in entries:
                if y_position < 50:
                    p.showPage()
                    y_position = 750
                
                p.drawString(50, y_position, f"Date: {entry.get('date', 'Unknown')}")
                y_position -= 20
                p.drawString(50, y_position, f"Time: {entry.get('timestamp', 'Unknown')}")
                y_position -= 20
                p.drawString(50, y_position, f"Type: {entry.get('type', 'Unknown')}")
                y_position -= 20
                
                content = entry.get('content', '')[:100] + "..." if len(entry.get('content', '')) > 100 else entry.get('content', '')
                p.drawString(50, y_position, f"Content: {content}")
                y_position -= 30
                
                if entry.get('analysis'):
                    analysis = entry.get('analysis', '')[:100] + "..." if len(entry.get('analysis', '')) > 100 else entry.get('analysis', '')
                    p.drawString(50, y_position, f"Analysis: {analysis}")
                    y_position -= 30
                
                y_position -= 20
            
            p.save()
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"PDF export error: {e}")
            raise Exception(f"Failed to create PDF export: {str(e)}")
    
    def export_to_json(self, entries):
        """Export entries to JSON format"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'entries': entries
            }
            
            buffer = io.BytesIO()
            buffer.write(json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8'))
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            raise Exception(f"Failed to create JSON export: {str(e)}")
    
    def get_export_filename(self, export_type):
        """Generate filename for export"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if export_type == 'pdf':
            return f"jarvis_diary_export_{timestamp}.pdf"
        elif export_type == 'json':
            return f"jarvis_diary_export_{timestamp}.json"
        else:
            return f"jarvis_diary_export_{timestamp}.txt"
    
    def get_export_mimetype(self, export_type):
        """Get MIME type for export"""
        if export_type == 'pdf':
            return 'application/pdf'
        elif export_type == 'json':
            return 'application/json'
        else:
            return 'text/plain'

"""
JARVIS AI Diary - Modular Flask Application
A sophisticated AI-powered diary system with voice recording and analysis capabilities
"""

from flask import Flask
import os
import logging
from dotenv import load_dotenv

# Import modular components
from modules.diary_manager import DiaryManager
from modules.ai_assistant import AIAssistant
from modules.audio_processor import AudioProcessor
from modules.export_manager import ExportManager
from modules.routes import RouteManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Ensure directories exist
    os.makedirs('daily_diary', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize configuration
    config = {
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY', ''),
        'OPENROUTER_MODELS': [
            "openai/gpt-3.5-turbo",
            "google/gemini-pro", 
            "anthropic/claude-3-haiku",
        ]
    }
    
    # Initialize modules
    diary_manager = DiaryManager()
    ai_assistant = AIAssistant(
        config['OPENROUTER_API_KEY'], 
        config['OPENROUTER_MODELS']
    )
    audio_processor = AudioProcessor()
    export_manager = ExportManager()
    
    # Initialize routes with all dependencies
    route_manager = RouteManager(
        app, 
        diary_manager, 
        ai_assistant, 
        audio_processor, 
        export_manager
    )
    
    return app, {
        'diary_manager': diary_manager,
        'ai_assistant': ai_assistant, 
        'audio_processor': audio_processor,
        'export_manager': export_manager
    }

# Create the Flask app
app, managers = create_app()

if __name__ == '__main__':
    audio_processor = managers['audio_processor']
    
    print(f"🎙️  JARVIS Neural Interface Starting...")
    print(f"📊  System Status:")
    print(f"   ✅ Speech Recognition: Available")
    print(f"   {'✅' if audio_processor.tts_available else '❌'} Text-to-Speech: {'Available' if audio_processor.tts_available else 'Not Available'}")
    print(f"   {'✅' if audio_processor.ffmpeg_available else '❌'} FFmpeg: {'Available' if audio_processor.ffmpeg_available else 'Not Available'}")
    
    if not audio_processor.ffmpeg_available:
        print(f"\n⚠️  WebM audio conversion requires FFmpeg. Install it for best results:")
        print(f"   Windows: winget install FFmpeg")
        print(f"   Or download from: https://ffmpeg.org/download.html")
    
    print(f"\n🚀  Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)

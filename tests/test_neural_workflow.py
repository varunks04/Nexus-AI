#!/usr/bin/env python3
"""
Test the exact scenario: simulate sending audio to the neural interface
and getting both text and voice response
"""

import sys
import os
import logging
import requests
import io

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.audio_processor import AudioProcessor
from modules.ai_assistant import AIAssistant
from modules.diary_manager import DiaryManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_neural_voice_workflow():
    """Test the complete neural voice workflow"""
    print("🎙️ Testing Neural Voice Workflow...")
    
    # Simulate the text that would come from voice transcription
    test_transcription = "Tell me something about Qutub Minar and Red Fort"
    
    print(f"📝 Simulated transcription: '{test_transcription}'")
    
    # Initialize components
    audio_processor = AudioProcessor()
    ai_assistant = AIAssistant()
    
    if not audio_processor.tts_available:
        print("❌ TTS not available!")
        return False
    
    print("✅ TTS is available")
    
    # Get AI response (same as the route does)
    print("\n🤖 Getting AI response...")
    try:
        ai_response = ai_assistant.get_ai_response(
            test_transcription, 
            "This is a voice diary entry. Respond as JARVIS with empathy and insight.",
            is_voice=True
        )
        print(f"✅ AI Response: '{ai_response[:100]}...'")
    except Exception as e:
        print(f"❌ AI response failed: {e}")
        return False
    
    # Test voice generation with user settings (same as the route does)
    print("\n🔊 Testing voice generation with user settings...")
    
    # Simulate user voice settings
    voice_settings = {
        'gender': 'male',
        'speed': 150,
        'volume': 100
    }
    
    print(f"🎛️ Using voice settings: {voice_settings}")
    
    try:
        voice_generated = audio_processor.speak_text_with_settings(
            ai_response,
            voice_settings['gender'], 
            voice_settings['speed'], 
            voice_settings['volume']
        )
        
        if voice_generated:
            print("✅ Voice generation successful!")
            print("🎯 This is exactly what should happen in the neural interface")
            return True
        else:
            print("❌ Voice generation failed")
            return False
            
    except Exception as tts_error:
        print(f"❌ TTS error: {tts_error}")
        # Test fallback
        print("🔄 Testing fallback to basic TTS...")
        try:
            voice_generated = audio_processor.speak_text(ai_response)
            if voice_generated:
                print("✅ Fallback TTS successful")
                return True
            else:
                print("❌ Fallback TTS also failed")
                return False
        except Exception as fallback_error:
            print(f"❌ Fallback error: {fallback_error}")
            return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 JARVIS Neural Voice Workflow Test")
    print("=" * 70)
    
    try:
        success = test_neural_voice_workflow()
        if success:
            print("\n✅ Neural voice workflow test passed!")
            print("🔍 If you're not hearing voice in the web interface,")
            print("   check the browser's audio settings and server logs.")
        else:
            print("\n❌ Neural voice workflow test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        logger.exception("Test failed with exception")
    
    print("\n" + "=" * 70)

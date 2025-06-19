#!/usr/bin/env python3
"""
Test TTS with exact same settings that the neural interface uses
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.audio_processor import AudioProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_user_voice_settings():
    """Load user voice settings from profile (same as in routes.py)"""
    try:
        import json
        profile_path = 'user_profile.json'
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
                return {
                    'gender': profile.get('voice_gender', 'male'),
                    'speed': profile.get('voice_speed', 150),
                    'volume': profile.get('voice_volume', 100)
                }
    except Exception as e:
        logger.warning(f"Could not load voice settings: {e}")
    
    # Default settings
    return {
        'gender': 'male',
        'speed': 150,
        'volume': 100
    }

def test_neural_interface_tts():
    """Test TTS exactly as the neural interface does"""
    print("🎙️ Testing Neural Interface TTS...")
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    if not audio_processor.tts_available:
        print("❌ TTS not available!")
        return False
    
    print("✅ TTS is available")
    
    # Load user voice settings (exactly as the route does)
    voice_settings = load_user_voice_settings()
    print(f"🎛️ Loaded voice settings: {voice_settings}")
    
    # Test with a typical AI response
    ai_response = "Sure! The Qutub Minar, located in Delhi, India, is one of the tallest brick minarets in the world, standing at about 73 meters high. It was constructed in 1192 by Qutb-ud-din Aibak and later completed by his successors. The Red Fort, also in Delhi, is a historic fort which was the main residence of the Mughal emperors for nearly 200 years. It's known for its massive enclosing walls of red sandstone and is an important symbol of India, hosting the annual Independence Day celebrations. Both sites are rich in history and are UNESCO World Heritage Sites."
    
    print("\n🔊 Speaking AI response with user settings...")
    print(f"📝 Response: '{ai_response[:100]}...'")
    
    # Test the exact method call that the route uses
    try:
        voice_generated = audio_processor.speak_text_with_settings(
            ai_response,
            voice_settings['gender'], 
            voice_settings['speed'], 
            voice_settings['volume']
        )
        
        if voice_generated:
            print("✅ TTS with settings successful!")
            print("🎯 This is EXACTLY what happens in the neural interface")
            print("🔍 If you didn't hear anything, check:")
            print("   - Windows audio mixer (make sure Python.exe isn't muted)")
            print("   - System volume levels")
            print("   - Audio output device selection")
            return True
        else:
            print("❌ TTS with settings failed")
            return False
            
    except Exception as tts_error:
        print(f"❌ TTS error: {tts_error}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Neural Interface TTS Test (Exact Simulation)")
    print("=" * 70)
    
    try:
        success = test_neural_interface_tts()
        if success:
            print("\n✅ Neural interface TTS test passed!")
            print("🎵 You should have heard JARVIS speaking")
        else:
            print("\n❌ Neural interface TTS test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        logger.exception("Test failed with exception")
    
    print("\n" + "=" * 70)

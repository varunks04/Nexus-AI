#!/usr/bin/env python3
"""
Direct test of TTS functionality to verify voice output is working
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

def test_tts_direct():
    """Test TTS functionality directly"""
    print("🎙️ Testing TTS Direct...")
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    if not audio_processor.tts_available:
        print("❌ TTS not available!")
        return False
    
    print("✅ TTS is available")
    
    # Test basic TTS
    print("\n🔊 Testing basic TTS...")
    test_text = "Hello! This is JARVIS testing the text to speech functionality."
    
    success = audio_processor.speak_text(test_text)
    if success:
        print("✅ Basic TTS test successful")
    else:
        print("❌ Basic TTS test failed")
        return False
    
    # Test TTS with custom settings (simulating AI response)
    print("\n🤖 Testing AI response TTS with custom settings...")
    ai_response = "I am JARVIS, your AI assistant. The neural voice interface is now functioning correctly."
    
    # Load user settings (simulate)
    user_settings = {
        "voice_gender": "male",
        "voice_speed": 150,
        "voice_volume": 80
    }
    
    success = audio_processor.speak_text_with_settings(
        ai_response,
        gender=user_settings.get("voice_gender", "male"),
        speed=user_settings.get("voice_speed", 150),
        volume=user_settings.get("voice_volume", 100)
    )
    
    if success:
        print("✅ AI response TTS test successful")
        print("🎯 Voice messages should now work in the web interface!")
    else:
        print("❌ AI response TTS test failed")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 JARVIS TTS Direct Test")
    print("=" * 60)
    
    try:
        success = test_tts_direct()
        if success:
            print("\n✅ All TTS tests passed!")
            print("🚀 The neural voice interface should now read out AI responses")
        else:
            print("\n❌ TTS tests failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        logger.exception("Test failed with exception")
    
    print("\n" + "=" * 60)

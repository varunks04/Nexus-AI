#!/usr/bin/env python3
"""
Test the TTS system with backup fallback
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

def test_tts_with_backup():
    """Test TTS system with backup fallback"""
    print("🎙️ Testing TTS with Backup Fallback...")
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    if not audio_processor.tts_available:
        print("❌ TTS not available!")
        return False
    
    print("✅ TTS is available")
    
    # Test 1: Basic TTS (will timeout but should fall back to backup)
    print("\n🔊 Test 1: Basic TTS with backup fallback...")
    test_text = "Testing TTS with automatic fallback to backup methods when primary TTS fails."
    
    success = audio_processor.speak_text(test_text)
    if success:
        print("✅ TTS successful (using primary or backup method)")
    else:
        print("❌ All TTS methods failed")
        return False
    
    # Test 2: AI response TTS with settings and backup
    print("\n🤖 Test 2: AI response TTS with backup...")
    ai_response = "I am JARVIS. The backup TTS system is now working to ensure you always hear AI responses."
    
    success = audio_processor.speak_text_with_settings(
        ai_response,
        gender="male",
        speed=150,
        volume=100
    )
    
    if success:
        print("✅ AI response TTS successful (using primary or backup method)")
        print("🎯 The neural voice interface should now work!")
    else:
        print("❌ All AI response TTS methods failed")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TTS with Backup Fallback Test")
    print("=" * 70)
    
    try:
        success = test_tts_with_backup()
        if success:
            print("\n✅ TTS with backup system working!")
            print("🚀 Neural voice interface should now provide voice feedback")
            print("📋 How it works:")
            print("   1. Tries pyttsx3 first (may timeout)")
            print("   2. Falls back to Windows SAPI (reliable)")
            print("   3. Falls back to PowerShell TTS (backup)")
        else:
            print("\n❌ TTS backup system failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        logger.exception("Test failed with exception")
    
    print("\n" + "=" * 70)

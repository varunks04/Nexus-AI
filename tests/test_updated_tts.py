#!/usr/bin/env python3
"""
Test the updated TTS system with timeout mechanism
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

def test_updated_tts():
    """Test the updated TTS system with timeout and debugging"""
    print("🎙️ Testing Updated TTS System...")
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    if not audio_processor.tts_available:
        print("❌ TTS not available!")
        return False
    
    print("✅ TTS is available")
    
    # Test 1: Basic TTS with timeout
    print("\n🔊 Test 1: Basic TTS with timeout mechanism...")
    test_text = "Testing the new timeout mechanism for JARVIS voice output."
    
    success = audio_processor.speak_text(test_text)
    if success:
        print("✅ Basic TTS with timeout successful")
    else:
        print("❌ Basic TTS with timeout failed")
        return False
    
    # Test 2: AI response TTS with custom settings and timeout
    print("\n🤖 Test 2: AI response TTS with timeout...")
    ai_response = "I am JARVIS. The timeout mechanism has been implemented to prevent TTS from hanging indefinitely."
    
    success = audio_processor.speak_text_with_settings(
        ai_response,
        gender="male",
        speed=150,
        volume=100
    )
    
    if success:
        print("✅ AI response TTS with timeout successful")
    else:
        print("❌ AI response TTS with timeout failed")
        return False
    
    # Test 3: Reset TTS state
    print("\n🔄 Test 3: TTS state reset...")
    audio_processor.force_reset_tts_state()
    print("✅ TTS state reset completed")
    
    # Test 4: TTS after reset
    print("\n🎵 Test 4: TTS after reset...")
    final_test = "TTS system has been successfully updated with timeout protection and debugging features."
    
    success = audio_processor.speak_text(final_test)
    if success:
        print("✅ TTS after reset successful")
        print("🎯 The neural voice interface should now work reliably!")
    else:
        print("❌ TTS after reset failed")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 JARVIS Updated TTS System Test")
    print("=" * 70)
    
    try:
        success = test_updated_tts()
        if success:
            print("\n✅ All TTS tests with timeout passed!")
            print("🚀 The neural voice interface should now work properly")
            print("📋 Changes made:")
            print("   - Added 10-second timeout to prevent TTS hanging")
            print("   - Added TTS engine reset on timeout/error")
            print("   - Added detailed text debugging")
            print("   - Added force reset method for stuck states")
        else:
            print("\n❌ TTS tests failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        logger.exception("Test failed with exception")
    
    print("\n" + "=" * 70)

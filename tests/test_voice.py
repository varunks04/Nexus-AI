"""
Debug script to test voice functionality
"""

import sys
sys.path.append('.')

from modules.audio_processor import AudioProcessor
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_voice():
    print("🔊 Testing JARVIS Voice System")
    
    # Initialize audio processor
    audio_processor = AudioProcessor()
    
    print(f"TTS Available: {audio_processor.tts_available}")
    
    if not audio_processor.tts_available:
        print("❌ TTS not available - this is the problem!")
        return
    
    # Test simple voice
    print("🎤 Testing basic voice...")
    result1 = audio_processor.speak_text("Hello, this is JARVIS testing basic voice functionality.")
    print(f"Basic voice result: {result1}")
    
    # Test voice with settings
    print("🎤 Testing voice with settings...")
    result2 = audio_processor.speak_text_with_settings(
        "Hello, this is JARVIS testing voice with custom settings.", 
        gender="male", 
        speed=150, 
        volume=80
    )
    print(f"Custom voice result: {result2}")
    
    # Test overlapping protection
    print("🎤 Testing overlapping protection...")
    result3 = audio_processor.speak_text("This should work.")
    result4 = audio_processor.speak_text("This should be skipped due to overlap.")
    print(f"First voice: {result3}, Second voice (should be False): {result4}")

if __name__ == "__main__":
    test_voice()

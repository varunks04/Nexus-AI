#!/usr/bin/env python3
"""
Alternative TTS test using Windows SAPI directly
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_windows_tts_direct():
    """Test Windows TTS directly without pyttsx3"""
    print("🎙️ Testing Windows TTS Directly...")
    
    try:
        # Try using Windows SAPI directly
        import win32com.client
        
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Test basic speech
        text = "Testing Windows SAPI directly. This should work without hanging."
        print(f"🔊 Speaking: '{text}'")
        
        result = speaker.Speak(text)
        print("✅ Windows SAPI TTS successful!")
        return True
        
    except ImportError:
        print("❌ win32com not available")
        return False
    except Exception as e:
        print(f"❌ Windows SAPI error: {e}")
        return False

def test_subprocess_tts():
    """Test TTS using Windows PowerShell"""
    print("\n🎙️ Testing PowerShell TTS...")
    
    try:
        import subprocess
        
        text = "Testing PowerShell text to speech. This is an alternative method."
        
        # Use PowerShell to speak
        cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\')"'
        
        print(f"🔊 Speaking via PowerShell: '{text[:50]}...'")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ PowerShell TTS successful!")
            return True
        else:
            print(f"❌ PowerShell TTS failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PowerShell TTS error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Alternative TTS Methods Test")
    print("=" * 70)
    
    success1 = test_windows_tts_direct()
    success2 = test_subprocess_tts()
    
    if success1 or success2:
        print("\n✅ At least one alternative TTS method works!")
        print("🔧 We can implement a backup TTS system")
    else:
        print("\n❌ All alternative TTS methods failed")
        print("🔍 This suggests a deeper Windows audio configuration issue")
    
    print("\n" + "=" * 70)

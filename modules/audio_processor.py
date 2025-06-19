"""
Audio Processing Module
Handles speech recognition, text-to-speech, and audio file processing
"""

import os
import re
import tempfile
import subprocess
import shutil
import logging
import speech_recognition as sr
import pyttsx3
import threading
import time
import sys

# Suppress Windows error dialogs for audio issues
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Disable Windows Error Reporting dialogs
        SEM_FAILCRITICALERRORS = 0x0001
        SEM_NOOPENFILEERRORBOX = 0x8000
        
        ctypes.windll.kernel32.SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX)
        
        # Also suppress console error dialogs
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.environ["PYTHONIOENCODING"] = "utf-8"
    except Exception as e:
        pass  # Ignore if this fails

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Initialize text-to-speech
        self.tts_available = self._init_tts()
        
        # Voice control to prevent overlapping speech
        self.is_speaking = False
        self.speech_lock = threading.Lock()
          # Check for FFmpeg
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _init_tts(self):
        """Initialize text-to-speech engine with masculine voice settings"""
        try:
            # Initialize with proper error handling to prevent Windows popups
            import sys
            if sys.platform == "win32":
                # Suppress Windows error reporting dialogs
                import os
                os.environ["PYTHONHTTPSVERIFY"] = "0"
            
            self.tts_engine = pyttsx3.init(driverName='sapi5' if sys.platform == "win32" else None)
            
            # Test if engine is functional before proceeding
            test_voices = self.tts_engine.getProperty('voices')
            if not test_voices:
                raise Exception("No TTS voices available")
            
            self.tts_engine.setProperty('rate', 140)  # Slower for deeper masculine tone
            self.tts_engine.setProperty('volume', 1.0)  # Full volume for authority
            
            # Get available voices and prioritize masculine/robotic voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Priority order: male voices, deeper voices, robotic voices
                voice_preferences = [
                    'david', 'mark', 'george', 'male', 'man', 'deep', 'bass',
                    'robotic', 'synthetic', 'computer', 'british', 'english'
                ]
                
                selected_voice = None
                for preference in voice_preferences:
                    for voice in voices:
                        if voice and hasattr(voice, 'name') and preference in voice.name.lower():
                            selected_voice = voice
                            break
                    if selected_voice:
                        break
                
                # Set the best masculine voice found, or default to first male voice
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice.id)
                    logger.info(f"Selected masculine voice: {selected_voice.name}")
                else:
                    # Fallback: try to avoid obviously female voices
                    for voice in voices:
                        if voice and hasattr(voice, 'name') and not any(fem in voice.name.lower() for fem in ['zira', 'hazel', 'female', 'woman', 'girl']):
                            self.tts_engine.setProperty('voice', voice.id)
                            logger.info(f"Fallback masculine voice: {voice.name}")
                            break
                    else:
                        # Last resort: use first available voice
                        if voices and voices[0]:
                            self.tts_engine.setProperty('voice', voices[0].id)
                            logger.info(f"Default voice: {voices[0].name}")
            
            # Test the engine with a simple call
            self.tts_engine.say("")
            self.tts_engine.runAndWait()
            
            return True
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
            self.tts_engine = None
            return False
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available in system PATH"""
        return shutil.which('ffmpeg') is not None
    
    def get_ffmpeg_install_instructions(self):
        """Return instructions for installing FFmpeg"""
        return """
        FFmpeg is required for audio conversion. Please install it:
        
        Windows:
        1. Download from https://ffmpeg.org/download.html
        2. Extract to a folder (e.g., C:\\ffmpeg)
        3. Add C:\\ffmpeg\\bin to your system PATH          Or use chocolatey: choco install ffmpeg        Or use winget: winget install FFmpeg        """
    
    def speak_text(self, text):
        """Convert text to speech with masculine robotic voice - thread safe"""
        if not self.tts_available or not self.tts_engine:
            logger.warning("TTS not available")
            return False        
        # Check if already speaking
        if self.is_speaking:
            logger.info("Speech in progress, skipping overlapping request")
            return False
        
        logger.info(f"Starting TTS for text: '{text[:50]}...'")
        
        # Add text debugging
        if not self.add_tts_text_debug(text, "speak_text"):
            return False
        
        with self.speech_lock:
            if self.is_speaking:  # Double-check inside lock
                logger.info("Speech already in progress after lock")
                return False
            
            self.is_speaking = True
            
            try:
                # Clean text for better speech
                clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
                
                # Skip empty text
                if not clean_text.strip():
                    logger.info("Empty text, skipping TTS")
                    return True
                
                logger.info(f"Clean text for TTS: '{clean_text}'")
                
                # Optimize TTS settings for masculine robotic voice
                self.tts_engine.setProperty('rate', 130)  # Slower for authoritative delivery
                self.tts_engine.setProperty('volume', 1.0)  # Full volume for presence
                
                # Ensure we're using a masculine voice
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Re-prioritize masculine voices each time for consistency
                    masculine_voice = None
                    for voice in voices:
                        if voice and hasattr(voice, 'name'):
                            # Check for masculine indicators
                            voice_name = voice.name.lower()
                            if any(masc in voice_name for masc in ['david', 'mark', 'george', 'male', 'man', 'deep', 'bass']):
                                masculine_voice = voice
                                break
                            elif 'british' in voice_name and 'female' not in voice_name:
                                masculine_voice = voice
                                break
                    
                    if masculine_voice:
                        self.tts_engine.setProperty('voice', masculine_voice.id)
                        logger.info(f"Using voice: {masculine_voice.name}")                
                # Generate speech with authoritative timing
                # Use try-catch specifically for pyttsx3 operations
                try:
                    logger.info("Starting TTS engine say and runAndWait")
                    self.tts_engine.say(clean_text)
                    
                    # Add timeout mechanism for runAndWait to prevent hanging
                    import threading
                    import time
                    
                    tts_completed = threading.Event()
                    tts_error_occurred = None
                    
                    def run_tts():
                        nonlocal tts_error_occurred
                        try:
                            self.tts_engine.runAndWait()
                            tts_completed.set()
                        except Exception as e:
                            tts_error_occurred = e
                            tts_completed.set()
                    
                    tts_thread = threading.Thread(target=run_tts, daemon=True)
                    tts_thread.start()
                      # Wait for TTS to complete with 10 second timeout
                    if tts_completed.wait(timeout=10.0):
                        if tts_error_occurred:
                            raise tts_error_occurred
                        logger.info("TTS engine completed successfully")
                    else:
                        logger.error("TTS engine timed out after 10 seconds")
                        # Force stop the TTS engine and reset state
                        try:
                            self.tts_engine.stop()
                        except:
                            pass
                        # Try backup TTS method
                        logger.info("Attempting backup TTS methods...")
                        if self.speak_text_sapi_backup(clean_text):
                            return True
                        elif self.speak_text_powershell_backup(clean_text):
                            return True
                        else:
                            logger.error("All TTS methods failed")
                            return False
                        
                except Exception as tts_error:
                    logger.error(f"TTS engine error: {tts_error}")
                    # Try to stop the engine and reset state
                    try:
                        self.tts_engine.stop()
                    except:
                        pass
                    # Try backup TTS method
                    logger.info("Attempting backup TTS methods...")
                    if self.speak_text_sapi_backup(clean_text):
                        return True
                    elif self.speak_text_powershell_backup(clean_text):
                        return True
                    else:
                        logger.error("All TTS methods failed")
                        return False
                
                # Add a small delay to ensure audio completes
                time.sleep(0.3)  # Reduced delay for better responsiveness
                
                logger.info("TTS completed successfully")
                return True
            except Exception as e:
                logger.error(f"TTS error: {e}")
                return False
            finally:
                self.is_speaking = False

    def convert_webm_to_wav_ffmpeg(self, webm_path, wav_path):
        """Convert WebM to WAV using FFmpeg"""
        try:
            cmd = [
                'ffmpeg', '-i', webm_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                wav_path,
                '-y'  # Overwrite output file
            ]
            
            # Create startup info to hide console window on Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {result.stderr}")
            
            return True
            
        except subprocess.TimeoutExpired:
            raise Exception("Audio conversion timed out")
        except FileNotFoundError:
            raise Exception("FFmpeg not found in system PATH")
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    def transcribe_audio_file(self, file_path):
        """Transcribe audio file using speech_recognition"""
        try:
            with sr.AudioFile(file_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio_data = self.recognizer.record(source)
            
            # Transcribe using Google Speech Recognition
            transcription = self.recognizer.recognize_google(
                audio_data, 
                language='en-US',
                show_all=False
            )
            return transcription
            
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {e}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def process_audio_file(self, file_path):
        """Process audio file and return transcription with metadata"""
        try:
            file_size = os.path.getsize(file_path)
            conversion_method = "direct"
            
            # Try direct transcription first
            try:
                transcription = self.transcribe_audio_file(file_path)
                return {
                    'transcription': transcription,
                    'file_size': file_size,
                    'conversion_method': conversion_method
                }
            except Exception as direct_error:
                logger.warning(f"Direct transcription failed: {direct_error}")
                
                # Try FFmpeg conversion if available
                if self.ffmpeg_available:
                    conversion_method = "ffmpeg"
                    wav_path = file_path.replace('.webm', '_converted.wav')
                    
                    try:
                        self.convert_webm_to_wav_ffmpeg(file_path, wav_path)
                        transcription = self.transcribe_audio_file(wav_path)
                        
                        # Clean up converted file
                        if os.path.exists(wav_path):
                            os.remove(wav_path)
                        
                        return {
                            'transcription': transcription,
                            'file_size': file_size,
                            'conversion_method': conversion_method
                        }
                    except Exception as ffmpeg_error:
                        logger.error(f"FFmpeg conversion failed: {ffmpeg_error}")
                        if os.path.exists(wav_path):
                            os.remove(wav_path)
                        raise ffmpeg_error
                else:
                    raise direct_error
                    
        except Exception as e:
            raise Exception(f"Audio processing failed: {str(e)}")
    
    def get_system_status(self):
        """Get system audio capabilities status"""
        return {
            'ffmpeg_available': self.ffmpeg_available,
            'tts_available': self.tts_available,
            'speech_recognition_available': True,
            'recommendations': {
                'install_ffmpeg': not self.ffmpeg_available,
                'ffmpeg_instructions': self.get_ffmpeg_install_instructions() if not self.ffmpeg_available else None
            }
        }

    def configure_voice_settings(self, gender="male", speed=150, volume=100):
        """Configure TTS voice settings with custom parameters"""
        if not self.tts_available:
            logger.warning("TTS not available for voice configuration")
            return False
        
        try:
            # Convert percentage volume to 0.0-1.0 range
            volume_normalized = max(0.0, min(1.0, volume / 100.0))
            
            # Set speed (WPM to pyttsx3 rate - typical range 100-300)
            # pyttsx3 rate is typically 100-300, so we'll use the WPM directly
            speed_clamped = max(80, min(300, speed))
            
            self.tts_engine.setProperty('rate', speed_clamped)
            self.tts_engine.setProperty('volume', volume_normalized)
            
            # Select voice based on gender preference
            voices = self.tts_engine.getProperty('voices')
            if voices:
                selected_voice = None
                
                if gender.lower() == "female":
                    # Look for female voices
                    female_indicators = ['zira', 'hazel', 'female', 'woman', 'girl', 'eva', 'susan', 'samantha']
                    for voice in voices:
                        voice_name = voice.name.lower()
                        if any(fem in voice_name for fem in female_indicators):
                            selected_voice = voice
                            break
                    
                    # If no explicitly female voice found, look for voices without male indicators
                    if not selected_voice:
                        male_indicators = ['david', 'mark', 'george', 'male', 'man']
                        for voice in voices:
                            voice_name = voice.name.lower()
                            if not any(male in voice_name for male in male_indicators):
                                selected_voice = voice
                                break
                
                else:  # Default to male
                    # Look for male voices (existing logic)
                    male_indicators = ['david', 'mark', 'george', 'male', 'man', 'deep', 'bass']
                    for voice in voices:
                        voice_name = voice.name.lower()
                        if any(male in voice_name for male in male_indicators):
                            selected_voice = voice
                            break
                
                # Apply the selected voice or fallback to first available
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice.id)
                    logger.info(f"Voice configured: {selected_voice.name}, Speed: {speed_clamped}, Volume: {volume}%")
                else:                    # Use first available voice as fallback
                    self.tts_engine.setProperty('voice', voices[0].id)
                    logger.info(f"Voice fallback: {voices[0].name}, Speed: {speed_clamped}, Volume: {volume}%")
            return True
        except Exception as e:
            logger.error(f"Voice configuration error: {e}")
            return False

    def speak_text_with_settings(self, text, gender="male", speed=150, volume=100):
        """Speak text with custom voice settings - thread safe"""
        if not self.tts_available or not self.tts_engine:
            logger.warning("TTS not available")
            return False
        
        # For important AI responses, wait briefly if speech is in progress rather than skipping
        import time
        max_wait_time = 3.0  # Maximum time to wait for current speech to finish
        wait_interval = 0.1
        waited_time = 0
        
        while self.is_speaking and waited_time < max_wait_time:
            logger.info(f"Waiting for current speech to finish... ({waited_time:.1f}s)")
            time.sleep(wait_interval)
            waited_time += wait_interval
        
        # If still speaking after wait time, skip this request
        if self.is_speaking:
            logger.warning("Speech still in progress after waiting, skipping AI response")
            return False        
        with self.speech_lock:
            if self.is_speaking:  # Double-check inside lock
                return False
            
            self.is_speaking = True
            
            try:
                logger.info(f"Starting AI response TTS with settings: gender={gender}, speed={speed}, volume={volume}")
                
                # Add text debugging
                if not self.add_tts_text_debug(text, f"AI_response_{gender}_{speed}_{volume}"):
                    return False
                
                # Configure voice with custom settings
                if not self.configure_voice_settings(gender, speed, volume):
                    return False
                
                # Clean text for better speech
                clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
                
                # Skip empty text
                if not clean_text.strip():
                    return True
                
                logger.info(f"Speaking AI response: '{clean_text[:100]}...'")
                
                # Generate speech with error handling and timeout
                try:
                    self.tts_engine.say(clean_text)
                    
                    # Add timeout mechanism for runAndWait to prevent hanging
                    import threading
                    
                    tts_completed = threading.Event()
                    tts_error_occurred = None
                    
                    def run_tts():
                        nonlocal tts_error_occurred
                        try:
                            self.tts_engine.runAndWait()
                            tts_completed.set()
                        except Exception as e:
                            tts_error_occurred = e
                            tts_completed.set()
                    
                    tts_thread = threading.Thread(target=run_tts, daemon=True)
                    tts_thread.start()                    # Wait for TTS to complete with 10 second timeout
                    if tts_completed.wait(timeout=10.0):
                        if tts_error_occurred:
                            raise tts_error_occurred
                        logger.info("AI response TTS completed successfully")
                    else:
                        logger.error("AI response TTS timed out after 10 seconds")
                        # Force stop the TTS engine
                        try:
                            self.tts_engine.stop()
                        except:
                            pass
                        # Try backup TTS method
                        logger.info("Attempting backup TTS for AI response...")
                        if self.speak_text_sapi_backup(clean_text):
                            return True
                        elif self.speak_text_powershell_backup(clean_text):
                            return True
                        else:
                            logger.error("All AI response TTS methods failed")
                            return False
                        
                except Exception as tts_error:
                    logger.error(f"TTS engine error with settings: {tts_error}")
                    # Try to stop the engine
                    try:
                        self.tts_engine.stop()
                    except:
                        pass
                    # Try backup TTS method
                    logger.info("Attempting backup TTS for AI response...")
                    if self.speak_text_sapi_backup(clean_text):
                        return True
                    elif self.speak_text_powershell_backup(clean_text):
                        return True
                    else:
                        logger.error("All AI response TTS methods failed")
                        return False
                
                # Add a small delay to ensure audio completes
                time.sleep(0.3)
                
                return True
            except Exception as e:
                logger.error(f"TTS with custom settings error: {e}")
                return False
            finally:
                self.is_speaking = False

    def get_available_voices(self):
        """Get list of available TTS voices with their properties"""
        if not self.tts_available:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'female' if any(fem in voice.name.lower() 
                                           for fem in ['zira', 'hazel', 'female', 'woman', 'girl', 'eva', 'susan', 'samantha'])
                             else 'male'
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def force_reset_tts_state(self):
        """Force reset TTS state when it gets stuck"""
        logger.warning("Force resetting TTS state")
        with self.speech_lock:
            self.is_speaking = False
            try:
                if self.tts_engine:
                    self.tts_engine.stop()
            except Exception as e:
                logger.warning(f"Error stopping TTS engine during reset: {e}")
            
            # Reinitialize TTS engine
            self.tts_available = self._init_tts()
            logger.info("TTS state reset completed")

    def add_tts_text_debug(self, text, context=""):
        """Add text debugging to help identify TTS issues"""
        logger.info(f"TTS DEBUG [{context}]: Text to speak: '{text[:200]}...' (Length: {len(text)} chars)")
        if not text.strip():
            logger.warning(f"TTS DEBUG [{context}]: Empty text provided")
            return False
        return True

    def speak_text_sapi_backup(self, text):
        """Backup TTS method using Windows SAPI directly"""
        try:
            import win32com.client
            
            logger.info(f"Using SAPI backup TTS for: '{text[:50]}...'")
            
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Set voice to masculine if available
            voices = speaker.GetVoices()
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_name = voice.GetDescription().lower()
                if any(male in voice_name for male in ['david', 'mark', 'male', 'man']):
                    speaker.Voice = voice
                    logger.info(f"SAPI backup using voice: {voice.GetDescription()}")
                    break
            
            # Speak the text (this method doesn't hang)
            speaker.Speak(text)
            logger.info("SAPI backup TTS completed successfully")
            return True
            
        except ImportError:
            logger.error("win32com not available for SAPI backup")
            return False
        except Exception as e:
            logger.error(f"SAPI backup TTS error: {e}")
            return False

    def speak_text_powershell_backup(self, text):
        """Backup TTS method using PowerShell"""
        try:
            import subprocess
            
            logger.info(f"Using PowerShell backup TTS for: '{text[:50]}...'")
            
            # Escape single quotes in text
            safe_text = text.replace("'", "''")
            
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{safe_text}\')"'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                logger.info("PowerShell backup TTS completed successfully")
                return True
            else:
                logger.error(f"PowerShell backup TTS failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"PowerShell backup TTS error: {e}")
            return False

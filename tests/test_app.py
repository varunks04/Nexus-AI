#!/usr/bin/env python3
"""
Test script to verify the JARVIS AI Diary application
"""

def test_imports():
    """Test all module imports"""
    try:
        print("🔍 Testing imports...")
        
        # Test Flask
        import flask
        print("✅ Flask imported successfully")
        
        # Test main modules
        from modules.diary_manager import DiaryManager
        print("✅ DiaryManager imported successfully")
        
        from modules.ai_assistant import AIAssistant
        print("✅ AIAssistant imported successfully")
        
        from modules.audio_processor import AudioProcessor
        print("✅ AudioProcessor imported successfully")
        
        from modules.export_manager import ExportManager
        print("✅ ExportManager imported successfully")
        
        from modules.routes import RouteManager
        print("✅ RouteManager imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    try:
        print("\n🏗️ Testing app creation...")
        
        from app import create_app
        app, managers = create_app()
        
        print("✅ Flask app created successfully")
        print(f"✅ Managers initialized: {list(managers.keys())}")
        
        # Test basic app configuration
        with app.app_context():
            print(f"✅ App name: {app.name}")
            print(f"✅ Secret key configured: {'Yes' if app.secret_key else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_modules():
    """Test individual module functionality"""
    try:
        print("\n🧪 Testing modules...")
        
        # Test DiaryManager
        from modules.diary_manager import DiaryManager
        diary_manager = DiaryManager()
        print("✅ DiaryManager initialized")
        
        # Test AudioProcessor
        from modules.audio_processor import AudioProcessor
        audio_processor = AudioProcessor()
        print("✅ AudioProcessor initialized")
        print(f"   TTS Available: {audio_processor.tts_available}")
        print(f"   FFmpeg Available: {audio_processor.ffmpeg_available}")
        
        return True
        
    except Exception as e:
        print(f"❌ Module test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎙️ JARVIS AI Diary - Application Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test app creation
    if not test_app_creation():
        success = False
    
    # Test modules
    if not test_modules():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Application is ready to run.")
        print("💡 To start the server, run: python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()

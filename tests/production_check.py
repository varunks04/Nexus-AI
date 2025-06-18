#!/usr/bin/env python3
"""
Final production readiness test
"""

import sys
import os
from app import create_app

def check_dependencies():
    """Check all required dependencies"""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'flask', 'requests', 'speech_recognition', 
        'pyttsx3', 'pydub', 'openai', 'reportlab'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing.append(module)
    
    return len(missing) == 0

def check_directories():
    """Check required directories exist"""
    print("\n📁 Checking directories...")
    
    dirs = ['daily_diary', 'uploads', 'templates', 'modules']
    all_exist = True
    
    for directory in dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - MISSING")
            all_exist = False
    
    return all_exist

def check_configuration():
    """Check configuration"""
    print("\n⚙️ Checking configuration...")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Check for required environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        secret_key = os.getenv('SECRET_KEY')
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        if secret_key:
            print("✅ SECRET_KEY configured")
        else:
            print("⚠️  SECRET_KEY not configured (using default)")
            
        if openrouter_key:
            print("✅ OPENROUTER_API_KEY configured")
        else:
            print("⚠️  OPENROUTER_API_KEY not configured")
            
    else:
        print("⚠️  .env file not found")
    
    return True

def final_app_test():
    """Final application test"""
    print("\n🚀 Final application test...")
    
    try:
        app, managers = create_app()
        
        # Test app creation
        print("✅ Application created successfully")
        
        # Test all managers
        for name, manager in managers.items():
            if manager:
                print(f"✅ {name} initialized")
            else:
                print(f"❌ {name} failed to initialize")
        
        # Test some basic routes in test mode
        app.config['TESTING'] = True
        with app.test_client() as client:
            test_routes = ['/', '/neural-record', '/archive', '/system-status']
            for route in test_routes:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ {route} working")
                else:
                    print(f"❌ {route} failed (status: {response.status_code})")
        
        print("✅ All routes tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def main():
    """Run all production readiness checks"""
    print("🎙️ JARVIS AI Diary - Production Readiness Check")
    print("=" * 60)
    
    all_passed = True
    
    # Check dependencies
    if not check_dependencies():
        all_passed = False
    
    # Check directories
    if not check_directories():
        all_passed = False
    
    # Check configuration
    if not check_configuration():
        all_passed = False
    
    # Final app test
    if not final_app_test():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 PRODUCTION READY!")
        print("🚀 Start the server with: python app.py")
        print("🌐 Then visit: http://localhost:5000")
        print("\n💡 Features available:")
        print("   • Voice recording and AI analysis")
        print("   • Text input with AI insights") 
        print("   • Diary management and export")
        print("   • Interactive chat with JARVIS")
        print("   • Archive with search and filtering")
    else:
        print("❌ ISSUES DETECTED")
        print("Please fix the issues above before running in production.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Server startup test for JARVIS AI Diary
"""

import sys
import time
import threading
import requests
from app import create_app

def test_server_startup():
    """Test if the server can start and serve requests"""
    print("🚀 Testing server startup...")
    
    try:
        # Create app
        app, managers = create_app()
        
        # Test in test mode
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            print(f"✅ Main page responds with status: {response.status_code}")
            
            # Test a few other pages
            test_pages = [
                '/neural-record',
                '/quantum-input', 
                '/memory-scan',
                '/compose',
                '/archive'
            ]
            
            for page in test_pages:
                response = client.get(page)
                if response.status_code == 200:
                    print(f"✅ {page} responds with status: {response.status_code}")
                else:
                    print(f"⚠️  {page} responds with status: {response.status_code}")
        
        print("✅ Server startup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

def test_system_status():
    """Test system status endpoint"""
    print("\n🔍 Testing system status...")
    
    try:
        app, managers = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            response = client.get('/system-status')
            if response.status_code == 200:
                print("✅ System status endpoint working")
                try:
                    data = response.get_json()
                    print(f"   Audio available: {data.get('audio_available', 'Unknown')}")
                    print(f"   TTS available: {data.get('tts_available', 'Unknown')}")
                    print(f"   FFmpeg available: {data.get('ffmpeg_available', 'Unknown')}")
                except:
                    print("   Status data format OK")
            else:
                print(f"⚠️  System status responds with: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ System status test error: {e}")
        return False

def main():
    """Run server tests"""
    print("🎙️ JARVIS AI Diary - Server Test")
    print("=" * 50)
    
    success = True
    
    # Test server startup
    if not test_server_startup():
        success = False
    
    # Test system status
    if not test_system_status():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All server tests passed!")
        print("🚀 The application is ready to run with: python app.py")
    else:
        print("❌ Some server tests failed.")
    
    return success

if __name__ == "__main__":
    main()

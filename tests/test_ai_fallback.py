"""
Test script to verify AI provider fallback system
"""

import sys
import os
sys.path.append('.')

from modules.ai_assistant import AIAssistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_fallback():
    """Test the AI fallback system"""
    print("🧠 Testing JARVIS AI Multi-Provider Fallback System\n")
    
    # Initialize with current configuration
    openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
    models = [
        "openai/gpt-3.5-turbo",
        "google/gemini-pro", 
        "anthropic/claude-3-haiku",
    ]
    
    ai_assistant = AIAssistant(openrouter_key, models)
    
    print(f"📡 Available API Providers: {len(ai_assistant.api_providers)}")
    for i, provider in enumerate(ai_assistant.api_providers, 1):
        status = "✅ Configured" if provider['api_key'] else "❌ Not configured"
        print(f"   {i}. {provider['name']}: {status} ({len(provider['models'])} models)")
    
    print(f"\n🔄 Testing AI response with fallback...")
    
    try:
        response = ai_assistant.get_ai_response(
            "Hello JARVIS, how are you today?", 
            is_voice=True
        )
        
        if response and "sorry" not in response.lower():
            print(f"✅ SUCCESS: AI responded successfully")
            print(f"💬 Response: {response[:100]}...")
        else:
            print(f"⚠️  FALLBACK: {response}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print(f"\n🧪 Testing analysis function...")
    
    try:
        analysis = ai_assistant.analyze_text(
            "I had a great day today, feeling very optimistic about the future.",
            "general"
        )
        
        if analysis and "unavailable" not in analysis.lower():
            print(f"✅ SUCCESS: Analysis completed")
            print(f"📊 Analysis: {analysis[:100]}...")
        else:
            print(f"⚠️  FALLBACK: {analysis}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print(f"\n✨ Test completed!")

if __name__ == "__main__":
    test_ai_fallback()

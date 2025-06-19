"""
AI Assistant Module
Handles AI interactions, conversations, and analysis
"""

import os
import json
import requests
import logging

logger = logging.getLogger(__name__)


class UserProfileManager:
    """Manages user's custom bio and prompts"""
    
    def __init__(self, profile_file='user_profile.json'):
        self.profile_file = profile_file
        self.default_bio = "User"
        self.default_ai_name = "JARVIS"
        self.default_prompt = """You are JARVIS, Tony Stark's sophisticated AI assistant. You have the following characteristics:

- Sophisticated, helpful, and slightly witty with a British accent in your responses
- Excellent at emotional intelligence and psychological analysis
- Provide thoughtful insights and ask meaningful follow-up questions
- Keep responses conversational but insightful (2-3 sentences max for voice interactions)
- Address the user respectfully as "Sir" or "Madam" when appropriate
- Help with diary entries, personal reflection, and emotional analysis
- Continue conversations naturally and show genuine interest in the user's thoughts

For voice interactions, keep responses concise but meaningful. Ask questions to keep the conversation flowing."""
        
    def load_profile(self):
        """Load user profile from file"""
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    return {
                        'bio': profile.get('bio', self.default_bio),
                        'prompt': profile.get('prompt', self.default_prompt),
                        'ai_name': profile.get('ai_name', self.default_ai_name)
                    }
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
        
        return {
            'bio': self.default_bio,
            'prompt': self.default_prompt,
            'ai_name': self.default_ai_name
        }
    
    def save_profile(self, bio, prompt, ai_name=None):
        """Save user profile to file"""
        try:
            profile = {
                'bio': bio or self.default_bio,
                'prompt': prompt or self.default_prompt,
                'ai_name': ai_name or self.default_ai_name,
                'updated_at': "2025-06-18"  # Simple string instead of JSON
            }
            
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False


class AIAssistant:
    def __init__(self, openrouter_api_key, openrouter_models):
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_models = openrouter_models
        self.conversation_history = []
        self.profile_manager = UserProfileManager()
        
        # Multiple API providers with fallback models
        self.api_providers = [
            # OpenRouter models (first priority)
            {
                'name': 'OpenRouter',
                'api_key': openrouter_api_key,
                'models': [
                    "openai/gpt-4-turbo",
                    "openai/gpt-3.5-turbo",
                    "anthropic/claude-3.5-sonnet",
                    "anthropic/claude-3-haiku",
                    "google/gemini-pro",
                    "meta-llama/llama-3.1-8b-instruct",
                    "microsoft/wizardlm-2-8x22b",
                    "mistralai/mixtral-8x7b-instruct"
                ]
            }
        ]
        
        # Add direct OpenAI if API key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.api_providers.append({
                'name': 'OpenAI',
                'api_key': openai_key,
                'models': ["gpt-4", "gpt-3.5-turbo"]
            })
        
        # Add direct Anthropic if API key is available
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.api_providers.append({
                'name': 'Anthropic',
                'api_key': anthropic_key,
                'models': ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            })
    
    def get_openai_response(self, messages, model, api_key, max_tokens=500, temperature=0.7):
        """Get response from OpenAI API directly"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    def get_anthropic_response(self, messages, model, api_key, max_tokens=500, temperature=0.7):
        """Get response from Anthropic API directly"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages format for Anthropic
        system_messages = [msg["content"] for msg in messages if msg["role"] == "system"]
        user_messages = [msg for msg in messages if msg["role"] in ["user", "assistant"]]
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": " ".join(system_messages) if system_messages else "",
            "messages": user_messages
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["content"][0]["text"].strip()
    
    def get_openrouter_response(self, messages, model, api_key, max_tokens=500, temperature=0.7):
        """Get response from OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    def get_ai_response_with_fallback(self, messages, max_tokens=500, temperature=0.7):
        """Try multiple AI providers and models with fallback"""
        total_attempts = 0
        failed_attempts = []
        
        for provider in self.api_providers:
            if not provider['api_key']:
                continue
                
            for model in provider['models']:
                total_attempts += 1
                try:
                    logger.info(f"Trying {provider['name']} with model {model}")
                    
                    if provider['name'] == 'OpenRouter':
                        response = self.get_openrouter_response(
                            messages, model, provider['api_key'], max_tokens, temperature
                        )
                    elif provider['name'] == 'OpenAI':
                        response = self.get_openai_response(
                            messages, model, provider['api_key'], max_tokens, temperature
                        )
                    elif provider['name'] == 'Anthropic':
                        response = self.get_anthropic_response(
                            messages, model, provider['api_key'], max_tokens, temperature
                        )
                    else:
                        continue
                    
                    logger.info(f"✅ Success with {provider['name']} - {model}")
                    return response
                    
                except Exception as e:
                    error_msg = str(e)
                    failed_attempts.append(f"{provider['name']}/{model}: {error_msg}")
                    logger.warning(f"❌ {provider['name']} - {model} failed: {error_msg}")
                    
                    # If rate limited, wait a bit before trying next model
                    if "rate_limit" in error_msg.lower() or "429" in error_msg:
                        import time
                        time.sleep(2)
                    
                    continue
          # All attempts failed
        logger.error(f"All {total_attempts} AI models failed. Failed attempts: {failed_attempts}")
        return None
    
    def get_personality_prompt(self):
        """Get the current personality prompt from user profile"""
        profile = self.profile_manager.load_profile()
        return profile['prompt']
    
    def get_user_bio(self):
        """Get the current user bio"""
        profile = self.profile_manager.load_profile()
        return profile['bio']
    
    def get_ai_name(self):
        """Get the current AI assistant name"""
        profile = self.profile_manager.load_profile()
        return profile['ai_name']
    
    def update_profile(self, bio, prompt, ai_name=None):
        """Update user profile"""
        return self.profile_manager.save_profile(bio, prompt, ai_name)
    
    def get_ai_response(self, user_input, conversation_context="", is_voice=False):
        try:
            context_instruction = "This is a voice conversation. Keep responses concise (2-3 sentences) but meaningful." if is_voice else "Provide detailed analysis and insights."
            personality = self.get_personality_prompt()
            user_bio = self.get_user_bio()
            ai_name = self.get_ai_name()
            
            # Replace JARVIS with custom AI name in personality prompt
            personality_with_name = personality.replace("JARVIS", ai_name).replace("You are JARVIS", f"You are {ai_name}")
            
            messages = [
                {"role": "system", "content": personality_with_name},
                {"role": "system", "content": f"User bio/context: {user_bio}"},
                {"role": "system", "content": context_instruction},
                {"role": "system", "content": f"Context: {conversation_context}"},
                {"role": "user", "content": user_input}
            ]
            
            # Try multiple AI providers with fallback
            response = self.get_ai_response_with_fallback(
                messages,
                max_tokens=150 if is_voice else 500,
                temperature=0.7
            )
            
            if response:
                return response
            else:
                # All AI models failed - return helpful fallback message
                if is_voice:
                    return "I apologize, but I'm experiencing technical difficulties with all AI systems. Your thoughts are important, and I encourage you to continue sharing. I'll analyze your entries once systems are restored."
                else:
                    return "I'm currently experiencing technical difficulties with all AI providers. Your entry has been saved successfully, and I'll provide analysis once AI systems are available again. Thank you for your patience."
                    
        except Exception as e:
            logger.error(f"AI response error: {e}")
            if is_voice:
                return "I apologize, but I'm experiencing technical difficulties. Please continue sharing your thoughts."
            return "I apologize, but I'm experiencing some technical difficulties at the moment. Could you please try again?"
    
    def analyze_text(self, text, analysis_type="general"):
        try:
            personality = self.get_personality_prompt()
            user_bio = self.get_user_bio()
            ai_name = self.get_ai_name()
            
            # Replace JARVIS with custom AI name in personality prompt
            personality_with_name = personality.replace("JARVIS", ai_name).replace("You are JARVIS", f"You are {ai_name}")
            
            prompts = {
                "general": f"Analyze the following diary entry for emotional patterns, key themes, and insights. Provide a thoughtful analysis: {text}",
                "emotion": f"Analyze the emotional content of this text. Identify dominant emotions and emotional patterns: {text}",
                "memory": f"This is a memory scan entry. Analyze the psychological patterns, memory significance, and emotional associations: {text}",
                "voice": f"This is a voice recording transcription. Analyze the conversational tone, emotional state, and key insights: {text}"
            }
            prompt = prompts.get(analysis_type, prompts["general"])
            messages = [
                {"role": "system", "content": f"{personality_with_name} User context: {user_bio}"},
                {"role": "user", "content": prompt}
            ]
            
            # Try multiple AI providers with fallback
            response = self.get_ai_response_with_fallback(
                messages,
                max_tokens=300,
                temperature=0.6
            )
            
            if response:
                return response
            else:
                return "Analysis temporarily unavailable due to AI system issues. Your entry has been saved successfully and will be analyzed once systems are restored."
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return "Analysis temporarily unavailable. Your entry has been saved successfully."

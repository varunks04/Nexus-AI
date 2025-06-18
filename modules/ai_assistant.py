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
        
    def get_openrouter_response(self, messages, max_tokens=500, temperature=0.7):
        """Get response from OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        last_error = None
        for model in self.openrouter_models:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e
        # If all models fail
        logger.error(f"All OpenRouter models failed: {last_error}")
        return "Sorry, all AI models are currently unavailable. Please try again later."
    
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
            response = self.get_openrouter_response(
                messages,
                max_tokens=150 if is_voice else 500,
                temperature=0.7
            )
            return response
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
            response = self.get_openrouter_response(
                messages,
                max_tokens=300,
                temperature=0.6
            )
            return response
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return "Analysis temporarily unavailable. Your entry has been saved successfully."

"""
Diary Management Module
Handles diary entries, file operations, and data management
"""

import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DiaryManager:
    def __init__(self, diary_folder='daily_diary'):
        self.diary_folder = diary_folder
        # Ensure directories exist
        os.makedirs(self.diary_folder, exist_ok=True)
        
    def get_today_filename(self):
        return datetime.now().strftime("%d-%m-%Y.txt")
    
    def get_filename_for_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d-%m-%Y.txt")
        except:
            return None
    
    def save_entry(self, content, entry_type="text_input", analysis="", date=None):
        if date:
            filename = self.get_filename_for_date(date)
        else:
            filename = self.get_today_filename()
            
        if not filename:
            return False
            
        filepath = os.path.join(self.diary_folder, filename)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = {
            'timestamp': timestamp,
            'type': entry_type,
            'content': content,
            'analysis': analysis,
            'date': date or datetime.now().strftime("%Y-%m-%d")
        }
        
        # Read existing entries
        entries = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entries.append(json.loads(line))
            except Exception as e:
                logger.error(f"Error reading existing entries in save_entry: {e}")
        
        # Add new entry
        entries.append(entry)
        
        # Write all entries back
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            logger.error(f"Error saving entry: {e}")
            return False
    
    def get_entries_for_date(self, date_str):
        filename = self.get_filename_for_date(date_str)
        if not filename:
            return []
            
        filepath = os.path.join(self.diary_folder, filename)
        entries = []
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entries.append(json.loads(line))
            except Exception as e:
                logger.error(f"Error reading entries: {e}")
        
        return entries
    
    def get_all_entries(self, start_date=None, end_date=None, entry_type=None, search_term=None):
        all_entries = []
        
        for filename in os.listdir(self.diary_folder):
            if filename.endswith('.txt'):
                try:
                    date_str = datetime.strptime(filename[:-4], "%d-%m-%Y").strftime("%Y-%m-%d")
                    
                    # Date filtering
                    if start_date and date_str < start_date:
                        continue
                    if end_date and date_str > end_date:
                        continue
                    
                    entries = self.get_entries_for_date(date_str)
                    for entry in entries:
                        # Type filtering
                        if entry_type and entry.get('type') != entry_type:
                            continue
                        
                        # Search filtering
                        if search_term:
                            search_lower = search_term.lower()
                            if (search_lower not in entry.get('content', '').lower() and 
                                search_lower not in entry.get('analysis', '').lower()):
                                continue
                        
                        entry['id'] = f"{date_str}_{entry['timestamp']}"
                        entry['date'] = date_str
                        all_entries.append(entry)
                        
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}")
                    continue
        
        # Sort by date and time (newest first)
        all_entries.sort(key=lambda x: (x['date'], x['timestamp']), reverse=True)
        return all_entries

    def update_entry(self, entry_id, new_content, ai_assistant):
        """Update a specific entry"""
        try:
            date_str, timestamp = entry_id.split('_', 1)
            filename = self.get_filename_for_date(date_str)
            
            if not filename:
                return False
            
            filepath = os.path.join(self.diary_folder, filename)
            
            if os.path.exists(filepath):
                entries = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if entry.get('timestamp') == timestamp:
                                entry['content'] = new_content
                                # Re-analyze the updated content
                                entry['analysis'] = ai_assistant.analyze_text(new_content, "general")
                            entries.append(entry)
                  # Write back all entries
                with open(filepath, 'w', encoding='utf-8') as f:
                    for entry in entries:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                return True
            return False
                
        except Exception as e:
            logger.error(f"Update entry error: {e}")
            return False
    
    def delete_entry(self, entry_id):
        """Delete a specific entry"""
        try:
            # Handle both formats: timestamp only or date_timestamp
            if '_' in entry_id:
                date_str, timestamp = entry_id.split('_', 1)
                filename = self.get_filename_for_date(date_str)
            else:
                # If only timestamp provided, search through all files
                timestamp = entry_id
                filename = None
                # Search through all diary files to find the entry
                for file in os.listdir(self.diary_folder):
                    if file.endswith('.txt'):
                        test_filepath = os.path.join(self.diary_folder, file)
                        try:
                            with open(test_filepath, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        entry = json.loads(line)
                                        if entry.get('timestamp') == timestamp:
                                            filename = file
                                            break
                                if filename:
                                    break
                        except:
                            continue
            
            if not filename:
                return False
            
            filepath = os.path.join(self.diary_folder, filename)
            
            if os.path.exists(filepath):
                entries = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if entry.get('timestamp') != timestamp:
                                entries.append(entry)
                
                # Write back remaining entries
                with open(filepath, 'w', encoding='utf-8') as f:
                    for entry in entries:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                return True
            return False
                
        except Exception as e:
            logger.error(f"Delete entry error: {e}")
            return False
    
    def get_entry_by_id(self, entry_id):
        """Get a specific entry by its ID (timestamp)"""
        try:
            # Search through all diary files
            for filename in os.listdir(self.diary_folder):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.diary_folder, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    entry = json.loads(line)
                                    if entry.get('timestamp') == entry_id or str(entry.get('timestamp')) == str(entry_id):
                                        # Add the ID field for easier handling
                                        entry['id'] = entry.get('timestamp')
                                        return entry
                    except Exception as e:
                        logger.error(f"Error reading file {filepath}: {e}")
                        continue
            return None
        except Exception as e:
            logger.error(f"Get entry by ID error: {e}")
            return None
        
    def load_user_profile(self):
        """Load user profile data from user_profile.json"""
        try:
            profile_path = 'user_profile.json'
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return default profile if file doesn't exist
                return {
                    'name': '',
                    'bio': '',
                    'ai_name': 'JARVIS',
                    'ai_personality': '',
                    'voice_settings': {
                        'gender': 'male',
                        'speed': 150,
                        'volume': 100
                    }
                }
        except Exception as e:
            logger.error(f"Load user profile error: {e}")
            return {}

    def save_user_profile(self, profile_data):
        """Save user profile data to user_profile.json"""
        try:
            profile_path = 'user_profile.json'
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Save user profile error: {e}")
            return False

"""
Flask Routes Module
Contains all Flask route definitions organized by functionality
"""

from flask import render_template, request, jsonify, redirect, url_for, send_file, flash
import logging
import datetime

logger = logging.getLogger(__name__)


class RouteManager:
    def __init__(self, app, diary_manager, ai_assistant, audio_processor, export_manager):
        self.app = app
        self.diary_manager = diary_manager
        self.ai_assistant = ai_assistant
        self.audio_processor = audio_processor
        self.export_manager = export_manager
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes with the Flask app"""
        
        # Main page routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/neural-record', 'neural_record', self.neural_record)
        self.app.add_url_rule('/quantum-input', 'quantum_input', self.quantum_input)
        self.app.add_url_rule('/memory-scan', 'memory_scan', self.memory_scan)
        self.app.add_url_rule('/data-sync', 'data_sync', self.data_sync)
        self.app.add_url_rule('/compose', 'compose', self.compose, methods=['GET', 'POST'])
        self.app.add_url_rule('/analyze', 'analyze', self.analyze)
        self.app.add_url_rule('/sync', 'sync', self.sync)
        self.app.add_url_rule('/archive', 'archive', self.archive)
        self.app.add_url_rule('/export', 'export', self.export)
        self.app.add_url_rule('/record', 'record', self.record)
        self.app.add_url_rule('/result', 'result', self.result)
        self.app.add_url_rule('/bio', 'bio_and_prompts', self.bio_and_prompts)
        
        # API routes
        self.app.add_url_rule('/transcribe_and_analyze_audio', 'transcribe_and_analyze_audio', 
                             self.transcribe_and_analyze_audio, methods=['POST'])
        self.app.add_url_rule('/system-status', 'system_status', self.system_status)
        self.app.add_url_rule('/chat', 'chat', self.chat, methods=['POST'])
        self.app.add_url_rule('/continue-conversation', 'continue_conversation', 
                             self.continue_conversation, methods=['POST'])
          # Voice feedback routes
        self.app.add_url_rule('/speak-greeting', 'speak_greeting', self.speak_greeting, methods=['POST'])
        self.app.add_url_rule('/speak-status', 'speak_status', self.speak_status, methods=['POST'])
        
        # Voice configuration routes
        self.app.add_url_rule('/test-voice', 'test_voice', self.test_voice, methods=['POST'])
        self.app.add_url_rule('/save-voice-settings', 'save_voice_settings', self.save_voice_settings, methods=['POST'])
        self.app.add_url_rule('/get-available-voices', 'get_available_voices', self.get_available_voices, methods=['GET'])
          # Form processing routes
        self.app.add_url_rule('/process-record', 'process_record', self.process_record, methods=['POST'])
        self.app.add_url_rule('/process-input', 'process_input', self.process_input, methods=['POST'])
        self.app.add_url_rule('/process-memory-scan', 'process_memory_scan', 
                             self.process_memory_scan, methods=['POST'])
        self.app.add_url_rule('/process-export', 'process_export', self.process_export, methods=['POST'])
        self.app.add_url_rule('/process-edited-text', 'process_edited_text', 
                             self.process_edited_text, methods=['POST'])
        self.app.add_url_rule('/save-entry', 'save_entry', self.save_entry, methods=['POST'])
        self.app.add_url_rule('/delete-entry', 'delete_entry', self.delete_entry, methods=['POST'])
        self.app.add_url_rule('/delete-entry/<entry_id>', 'delete_entry_api', self.delete_entry_api, methods=['DELETE'])
        self.app.add_url_rule('/edit-entry/<entry_id>', 'edit_entry', self.edit_entry, methods=['GET'])
        self.app.add_url_rule('/update-profile', 'update_profile', self.update_profile, methods=['POST'])
        
        # Error handlers
        self.app.errorhandler(404)(self.not_found_error)
        self.app.errorhandler(500)(self.internal_error)
    
    # Voice Feedback Functions
    def speak_greeting(self):
        """Generate and speak a personalized greeting"""
        try:
            data = request.get_json() if request.is_json else {}
            greeting_type = data.get('type', 'general')
            user_name = data.get('user_name', '')
            
            # Get current time for contextual greeting
            current_hour = datetime.datetime.now().hour
            
            if current_hour < 12:
                time_greeting = "Good morning"
            elif current_hour < 17:
                time_greeting = "Good afternoon"
            else:
                time_greeting = "Good evening"
              # Create personalized greeting based on type
            if greeting_type == 'startup':
                greeting = f"{time_greeting}! JARVIS neural interface is now online and ready for voice interaction. How may I assist you today?"
            elif greeting_type == 'neural_record':
                greeting = f"{time_greeting}! Welcome to the neural voice interface. I'm ready to listen and analyze your thoughts. Please speak when ready."
            elif greeting_type == 'returning':
                greeting = f"Welcome back! JARVIS systems are fully operational. What would you like to explore today?"
            elif greeting_type == 'status_only':
                # Minimal status update, no voice - just return ready status
                greeting = "Neural interface ready for voice capture"
                voice_success = True  # Don't actually speak, just return success
                return jsonify({
                    'success': True,
                    'greeting': greeting,
                    'voice_generated': False,  # No voice for status-only
                    'timestamp': datetime.datetime.now().isoformat()
                })
            else:
                greeting = f"{time_greeting}! I'm JARVIS, your AI assistant. How can I help you today?"
            
            if user_name:
                greeting = greeting.replace("!", f", {user_name}!")
            
            # Generate voice output
            voice_success = self.audio_processor.speak_text(greeting)
            
            return jsonify({
                'success': True,
                'greeting': greeting,
                'voice_generated': voice_success,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Greeting generation error: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to generate greeting: {str(e)}'
            }), 500

    def speak_status(self):
        """Generate and speak status updates for various operations"""
        try:
            data = request.get_json()
            status_type = data.get('type', '')
            success = data.get('success', True)
            details = data.get('details', {})
            
            # Generate appropriate status message based on type and success
            if status_type == 'export':
                if success:
                    export_type = details.get('export_type', 'file')
                    message = f"Export completed successfully! Your {export_type} has been generated and should be available in your downloads folder."
                else:
                    message = "Export failed. Please check your settings and try again."
                    
            elif status_type == 'analysis':
                if success:
                    message = "Analysis completed successfully! Here are your results. The analysis has been saved to your diary."
                else:
                    message = "Analysis could not be completed due to technical difficulties. Your entry has been saved for later processing."
                    
            elif status_type == 'save_entry':
                if success:
                    message = "Your diary entry has been successfully saved and analyzed. Thank you for sharing your thoughts with me."
                else:
                    message = "There was an issue saving your entry. Please try again or check your connection."
                    
            elif status_type == 'voice_processing':
                if success:
                    message = "Voice processing completed successfully. Your audio has been transcribed and analyzed."
                else:
                    message = "Voice processing encountered an error. Please ensure your microphone is working and try again."
                    
            elif status_type == 'chat_session':
                if success:
                    message = "Chat session logged successfully. Our conversation has been saved to your diary."
                else:
                    message = "Unable to log chat session. Your conversation may not have been saved."
                    
            elif status_type == 'memory_scan':
                if success:
                    insights_count = details.get('insights_count', 0)
                    message = f"Memory scan completed! I've identified {insights_count} key insights from your past entries."
                else:
                    message = "Memory scan could not be completed. Please try again later."
                    
            elif status_type == 'sync':
                if success:
                    synced_count = details.get('synced_count', 0)
                    message = f"Data synchronization successful! {synced_count} entries have been synchronized."
                else:
                    message = "Synchronization failed. Please check your connection and try again."
                    
            elif status_type == 'backup':
                if success:
                    message = "Backup completed successfully! Your data is now safely stored."
                else:
                    message = "Backup failed. Please ensure you have sufficient storage space and try again."
                    
            elif status_type == 'profile_update':
                if success:
                    message = "Profile updated successfully! Your preferences have been saved and I've adapted to your new settings."
                else:
                    message = "Profile update failed. Please check your inputs and try again."
                    
            elif status_type == 'system_ready':
                message = "All systems are operational. JARVIS is ready for your commands."
                
            elif status_type == 'recording_start':
                message = "Recording started. I'm listening carefully to your voice."
                
            elif status_type == 'recording_stop':
                message = "Recording stopped. Processing your audio now."
                
            elif status_type == 'conversation_end':
                message = "Conversation session ended. It was a pleasure talking with you. Your session has been saved."
                
            elif status_type == 'error_recovery':
                message = "System recovered from error. All functions are now operational again."
                
            else:
                # Generic status message
                if success:
                    message = f"Operation completed successfully!"
                else:
                    message = f"Operation failed. Please try again."
            
            # Add additional details if provided
            additional_info = details.get('additional_info', '')
            if additional_info:
                message += f" {additional_info}"
            
            # Generate voice output
            voice_success = self.audio_processor.speak_text(message)
            
            return jsonify({
                'success': True,
                'message': message,
                'voice_generated': voice_success,
                'status_type': status_type,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Status message generation error: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to generate status message: {str(e)}'
            }), 500

    def _speak_success_message(self, operation_type, details=None):
        """Helper function to speak success messages for various operations"""
        try:
            success_data = {
                'type': operation_type,
                'success': True,
                'details': details or {}
            }
            
            # Call the speak_status function internally
            with self.app.test_request_context(json=success_data):
                result = self.speak_status()
                return result.get_json().get('voice_generated', False)
                
        except Exception as e:
            logger.error(f"Internal speak success error: {e}")
            return False

    def _speak_error_message(self, operation_type, error_details=None):
        """Helper function to speak error messages for various operations"""
        try:
            error_data = {
                'type': operation_type,
                'success': False,
                'details': error_details or {}
            }
            
            # Call the speak_status function internally
            with self.app.test_request_context(json=error_data):
                result = self.speak_status()
                return result.get_json().get('voice_generated', False)
                
        except Exception as e:
            logger.error(f"Internal speak error error: {e}")
            return False
    
    # Template routes
    def index(self):
        return render_template('index.html')
    
    def neural_record(self):
        ai_name = self.ai_assistant.get_ai_name()
        return render_template('neural_record.html', ai_name=ai_name)
    
    def quantum_input(self):
        return render_template('quantum_input.html')
    
    def memory_scan(self):
        return render_template('memory_scan.html')
    
    def data_sync(self):
        return render_template('data_sync.html')
    
    def compose(self):
        """Handle compose page - GET renders form, POST handled by save_entry"""
        return render_template('compose.html')
    
    def analyze(self):
        return render_template('analyze.html')
    
    def sync(self):
        return render_template('sync.html')
    
    def export(self):
        return render_template('export.html')
    
    def record(self):
        return render_template('record.html')
    
    def result(self):
        return render_template('result.html')
    
    def bio_and_prompts(self):
        """Bio and prompts editing page"""
        try:
            profile = self.ai_assistant.profile_manager.load_profile()
            return render_template('bio_and_prompts.html', 
                                 current_bio=profile['bio'], 
                                 current_prompt=profile['prompt'],
                                 current_ai_name=profile['ai_name'])
        except Exception as e:
            logger.error(f"Bio and prompts page error: {e}")
            return render_template('bio_and_prompts.html', 
                                 current_bio='', 
                                 current_prompt='',
                                 current_ai_name='JARVIS')
    
    def archive(self):
        """Archive page with filtering"""
        try:
            # Get query parameters for filtering
            page = request.args.get('page', 1, type=int)
            search = request.args.get('search', '')
            entry_type = request.args.get('entryType', '')
            date = request.args.get('date', '')
            
            # Get entries with filters
            entries = self.diary_manager.get_all_entries(
                search_term=search if search else None,
                entry_type=entry_type if entry_type else None
            )
            
            # Pagination
            per_page = 10
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_entries = entries[start_idx:end_idx]
            total_pages = (len(entries) + per_page - 1) // per_page
            
            return render_template('archive.html', 
                                 entries=paginated_entries, 
                                 page=page, 
                                 total_pages=total_pages,
                                 search=search,
                                 entryType=entry_type,
                                 date=date)
        except Exception as e:
            logger.error(f"Archive page error: {e}")
            return render_template('archive.html', 
                                 entries=[], 
                                 page=1, 
                                 total_pages=1,
                                 search='',
                                 entryType='',
                                 date='')
    
    # API routes
    def transcribe_and_analyze_audio(self):
        """Handle audio transcription and analysis"""
        try:
            if 'audio' not in request.files:
                return jsonify({'status': 'error', 'message': 'No audio file provided'})
            
            audio_file = request.files['audio']
            
            if audio_file.filename == '':
                return jsonify({'status': 'error', 'message': 'No audio file selected'})
            
            # Process audio file
            audio_result = self.audio_processor.process_audio_file(audio_file)
            transcription = audio_result['transcription']
            
            # Get AI analysis and response
            try:
                # Get JARVIS analysis
                analysis = self.ai_assistant.analyze_text(transcription, "voice")
                
                # Get conversational response from JARVIS
                ai_response = self.ai_assistant.get_ai_response(
                    transcription, 
                    "This is a voice diary entry. Respond as JARVIS with empathy and insight.",
                    is_voice=True
                )
                
                logger.info("AI processing successful")
                
            except Exception as ai_error:
                logger.error(f"AI processing error: {ai_error}")
                analysis = "AI analysis temporarily unavailable due to API issues."
                ai_response = "Thank you for sharing your thoughts. Your entry has been recorded successfully, though I'm experiencing some technical difficulties with my analysis systems."
            
            # Save to diary
            try:
                full_entry = f"Voice Entry: {transcription}\n\nJARVIS Response: {ai_response}"
                success = self.diary_manager.save_entry(full_entry, "voice_record", analysis)
                
                if not success:
                    logger.warning("Failed to save voice entry to diary")
                    
            except Exception as save_error:
                logger.error(f"Save error: {save_error}")
            
            # Generate voice response (optional)
            voice_generated = False
            try:
                voice_generated = self.audio_processor.speak_text(ai_response)
            except Exception as tts_error:
                logger.error(f"TTS error: {tts_error}")
            
            return jsonify({
                'status': 'success',
                'transcribed_text': transcription,
                'analysis': analysis,
                'ai_response': ai_response,
                'voice_generated': voice_generated,
                'conversion_method': audio_result['conversion_method'],
                'file_size': audio_result['file_size'],
                'message': 'Voice entry processed and saved successfully'
            })
            
        except Exception as e:
            logger.error(f"Unexpected error in audio processing: {e}")
            return jsonify({
                'status': 'error', 
                'message': f'An unexpected error occurred: {str(e)}'
            })
    
    def system_status(self):
        """System status check"""
        try:
            return jsonify(self.audio_processor.get_system_status())
        except Exception as e:
            logger.error(f"System status error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Unable to get system status: {str(e)}'
            })
    
    def chat(self):
        """Interactive chat endpoint"""
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            conversation_id = data.get('conversation_id', 'default')
            
            if not user_message:
                return jsonify({'error': 'No message provided'})
            
            # Get conversation context (last few messages)
            context = ""
            
            # Get AI response for conversation
            ai_response = self.ai_assistant.get_ai_response(
                user_message, 
                context,
                is_voice=True
            )
            
            # Log the conversation to today's diary
            conversation_entry = f"Chat Session:\nUser: {user_message}\nJARVIS: {ai_response}"
            self.diary_manager.save_entry(conversation_entry, "chat_session", "Interactive conversation with JARVIS")
            
            # Generate voice response if available
            voice_generated = False
            try:
                voice_generated = self.audio_processor.speak_text(ai_response)
            except Exception as tts_error:
                logger.error(f"TTS error in chat: {tts_error}")
            
            return jsonify({
                'response': ai_response,
                'voice_generated': voice_generated,
                'logged': True
            })
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({'error': f'Chat error: {str(e)}'})
    
    def continue_conversation(self):
        """Continue conversation endpoint"""
        try:
            data = request.get_json()
            conversation_history = data.get('conversation_history', [])
            
            if not conversation_history:
                return jsonify({'error': 'No conversation history provided'})
            
            # Create context from conversation history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
            
            # Generate a follow-up question or comment to continue the conversation
            follow_up_prompt = "Based on our conversation, ask a thoughtful follow-up question or make an insightful comment to continue our discussion."
            
            ai_response = self.ai_assistant.get_ai_response(
                follow_up_prompt,
                context,
                is_voice=True
            )
            
            # Generate voice response
            voice_generated = False
            try:
                voice_generated = self.audio_processor.speak_text(ai_response)
            except Exception as tts_error:
                logger.error(f"TTS error in continue conversation: {tts_error}")
            
            return jsonify({
                'response': ai_response,
                'voice_generated': voice_generated
            })
            
        except Exception as e:
            logger.error(f"Continue conversation error: {e}")
            return jsonify({'error': f'Conversation error: {str(e)}'})
    
    # Form processing routes
    def save_entry(self):
        """Save entry from compose form with AI feedback workflow"""
        try:
            data = request.get_json() if request.is_json else request.form
            content = data.get('content', '').strip()
            
            if not content:
                self._speak_error_message('save_entry', {'additional_info': 'Please provide some content before saving.'})
                return jsonify({'error': 'Content cannot be empty'}), 400
            
            # Step 1: Get AI analysis first
            try:
                analysis = self.ai_assistant.analyze_text(content, "general")
            except Exception as ai_error:
                logger.error(f"AI analysis error: {ai_error}")
                analysis = "AI analysis unavailable - processing offline"
            
            # Step 2: Generate AI response for voice feedback
            try:
                ai_response = self.ai_assistant.get_ai_response(
                    content, 
                    "Provide thoughtful feedback on this diary entry. Be encouraging and insightful.",
                    is_voice=True
                )
            except Exception as ai_error:
                logger.error(f"AI response error: {ai_error}")
                ai_response = "Thank you for sharing your thoughts. Your entry has been analyzed and saved successfully."
            
            # Step 3: Generate voice feedback FIRST
            voice_success = False
            try:
                voice_success = self.audio_processor.speak_text(ai_response)
                logger.info(f"Voice feedback generated: {voice_success}")
            except Exception as voice_error:
                logger.error(f"Voice generation error: {voice_error}")
            
            # Step 4: Save entry to diary ONLY AFTER voice feedback
            try:
                success = self.diary_manager.save_entry(
                    content=content,
                    entry_type='text_input',
                    analysis=analysis
                )
            except Exception as save_error:
                logger.error(f"Save entry error: {save_error}")
                success = False
            
            if success:
                # Speak success message
                self._speak_success_message('save_entry')
                
                return jsonify({
                    'success': True,
                    'message': 'Entry saved successfully after AI feedback',
                    'analysis': analysis,
                    'ai_response': ai_response,
                    'voice_generated': voice_success
                })
            else:
                self._speak_error_message('save_entry')
                return jsonify({'error': 'Failed to save entry to diary'}), 500
                
        except Exception as e:
            logger.error(f"Save entry processing error: {e}")
            self._speak_error_message('save_entry', {'additional_info': str(e)})
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    def process_record(self):
        """Process record form"""
        try:
            content = request.form.get('content', '')
            if not content:
                flash('Please enter some content', 'error')
                return redirect(url_for('record'))
            
            # Get AI analysis
            analysis = self.ai_assistant.analyze_text(content, "general")
            
            # Save to diary
            success = self.diary_manager.save_entry(content, "text_input", analysis)
            
            if success:
                flash('Entry saved successfully!', 'success')
                self._speak_success_message('save_entry')
            else:
                flash('Error saving entry', 'error')
                self._speak_error_message('save_entry')
                
            return redirect(url_for('result'))
            
        except Exception as e:
            logger.error(f"Process record error: {e}")
            flash('An error occurred while processing your entry', 'error')
            self._speak_error_message('save_entry', {'additional_info': str(e)})
            return redirect(url_for('record'))
    
    def process_input(self):
        """Process quantum input form"""
        try:
            content = request.form.get('content', '')
            if not content:
                flash('Please enter some content', 'error')
                return redirect(url_for('quantum_input'))
            
            # Get AI analysis
            analysis = self.ai_assistant.analyze_text(content, "general")
            
            # Save to diary
            success = self.diary_manager.save_entry(content, "quantum_input", analysis)
            
            if success:
                flash('Quantum input processed successfully!', 'success')
                self._speak_success_message('analysis')
            else:
                flash('Error processing input', 'error')
                self._speak_error_message('analysis')
                
            return redirect(url_for('result'))
            
        except Exception as e:
            logger.error(f"Process input error: {e}")
            flash('An error occurred while processing your input', 'error')
            self._speak_error_message('analysis', {'additional_info': str(e)})
            return redirect(url_for('quantum_input'))
    
    def process_memory_scan(self):
        """Process memory scan form"""
        try:
            content = request.form.get('content', '')
            if not content:
                flash('Please enter some content', 'error')
                return redirect(url_for('memory_scan'))
            
            # Get AI analysis
            analysis = self.ai_assistant.analyze_text(content, "memory")
            
            # Save to diary
            success = self.diary_manager.save_entry(content, "memory_scan", analysis)
            
            if success:
                flash('Memory scan completed successfully!', 'success')
                self._speak_success_message('memory_scan', {'insights_count': 1})
            else:
                flash('Error processing memory scan', 'error')
                self._speak_error_message('memory_scan')
                
            return redirect(url_for('result'))
            
        except Exception as e:
            logger.error(f"Process memory scan error: {e}")
            flash('An error occurred while processing your memory scan', 'error')
            self._speak_error_message('memory_scan', {'additional_info': str(e)})
            return redirect(url_for('memory_scan'))
    
    def process_export(self):
        """Process export form with voice feedback"""
        try:
            export_type = request.form.get('export_type', 'pdf')
            start_date = request.form.get('start_date', '')
            end_date = request.form.get('end_date', '')
            
            # Get entries for export
            entries = self.diary_manager.get_all_entries(
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None
            )
            
            if export_type == 'pdf':
                buffer = self.export_manager.export_to_pdf(entries)
            elif export_type == 'json':
                buffer = self.export_manager.export_to_json(entries)
            else:
                self._speak_error_message('export', {'additional_info': 'Invalid export format selected.'})
                flash('Invalid export type', 'error')
                return redirect(url_for('export'))
            
            # Speak success message
            self._speak_success_message('export', {
                'export_type': export_type.upper(),
                'entries_count': len(entries)
            })
            
            filename = self.export_manager.get_export_filename(export_type)
            mimetype = self.export_manager.get_export_mimetype(export_type)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            self._speak_error_message('export', {'additional_info': str(e)})
            flash('An error occurred during export', 'error')
            return redirect(url_for('export'))
    
    def process_edited_text(self):
        """Process edited text form"""
        try:
            entry_id = request.form.get('entry_id', '')
            content = request.form.get('content', '')
            
            if not entry_id or not content:
                flash('Missing entry ID or content', 'error')
                return redirect(url_for('archive'))
            
            success = self.diary_manager.update_entry(entry_id, content, self.ai_assistant)
            
            if success:
                flash('Entry updated successfully!', 'success')
                self._speak_success_message('save_entry')
            else:
                flash('Error updating entry', 'error')
                self._speak_error_message('save_entry')
                
            return redirect(url_for('archive'))
            
        except Exception as e:
            logger.error(f"Process edited text error: {e}")
            flash('An error occurred while updating the entry', 'error')
            self._speak_error_message('save_entry', {'additional_info': str(e)})
            return redirect(url_for('archive'))
    
    def delete_entry(self):
        """Delete entry"""
        try:
            entry_id = request.form.get('entry_id', '')
            
            if not entry_id:
                return jsonify({'error': 'Missing entry ID'})
            
            success = self.diary_manager.delete_entry(entry_id)
            
            if success:
                return jsonify({'success': True, 'message': 'Entry deleted successfully'})
            else:
                return jsonify({'error': 'Entry not found'})
                
        except Exception as e:
            logger.error(f"Delete entry error: {e}")
            return jsonify({'error': 'An error occurred while deleting the entry'})
    
    def edit_entry(self, entry_id):
        """Edit entry page"""
        try:
            # Get the entry data
            entry = self.diary_manager.get_entry_by_id(entry_id)
            if not entry:
                flash('Entry not found', 'error')
                return redirect(url_for('archive'))
            
            return render_template('edit_text.html', entry=entry)
            
        except Exception as e:
            logger.error(f"Edit entry error: {e}")
            flash('An error occurred while loading the entry', 'error')
            return redirect(url_for('archive'))
    
    def delete_entry_api(self, entry_id):
        """Delete entry by ID (API endpoint)"""
        try:
            if not entry_id:
                return jsonify({'error': 'Missing entry ID'})
            
            success = self.diary_manager.delete_entry(entry_id)
            
            if success:
                return jsonify({'success': True, 'message': 'Entry deleted successfully'})
            else:
                return jsonify({'error': 'Entry not found'})
                
        except Exception as e:
            logger.error(f"Delete entry API error: {e}")
            return jsonify({'error': 'An error occurred while deleting the entry'})
    
    def update_profile(self):
        """Update user profile (bio, prompt, and AI name)"""
        try:
            bio = request.form.get('bio', '').strip()
            prompt = request.form.get('prompt', '').strip()
            ai_name = request.form.get('ai_name', '').strip()
            
            success = self.ai_assistant.update_profile(bio, prompt, ai_name)
            
            if success:
                flash('Profile updated successfully!', 'success')
                self._speak_success_message('profile_update')
            else:
                flash('Error updating profile', 'error')
                self._speak_error_message('profile_update')
                
            return redirect(url_for('bio_and_prompts'))
            
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            flash('An error occurred while updating your profile', 'error')
            self._speak_error_message('profile_update', {'additional_info': str(e)})
            return redirect(url_for('bio_and_prompts'))
    
    # Error handlers
    def not_found_error(self, error):
        return render_template('error.html', message='Page not found'), 404
    
    def internal_error(self, error):
        return render_template('error.html', message='Internal server error'), 500

    # Voice Configuration Functions
    def test_voice(self):
        """Test voice settings with a sample message"""
        try:
            data = request.get_json() if request.is_json else {}
            
            # Get voice settings from request
            gender = data.get('gender', 'male')
            speed = int(data.get('speed', 150))
            volume = int(data.get('volume', 100))
            
            # Validate settings
            if gender not in ['male', 'female']:
                gender = 'male'
            
            speed = max(80, min(300, speed))
            volume = max(0, min(100, volume))
            
            # Test message
            test_message = f"Hello! This is JARVIS testing your voice settings. Gender: {gender}, Speed: {speed} words per minute, Volume: {volume} percent."
            
            # Use custom voice settings to speak the test message
            voice_success = self.audio_processor.speak_text_with_settings(
                test_message, gender, speed, volume
            )
            
            return jsonify({
                'success': voice_success,
                'message': 'Voice test completed' if voice_success else 'Voice test failed',
                'settings': {
                    'gender': gender,
                    'speed': speed,
                    'volume': volume
                }
            })
            
        except Exception as e:
            logger.error(f"Voice test error: {e}")
            return jsonify({
                'success': False,
                'message': f'Voice test failed: {str(e)}',
                'settings': {}
            }), 500

    def save_voice_settings(self):
        """Save voice settings to user profile"""
        try:
            data = request.get_json() if request.is_json else {}
            
            # Get voice settings from request
            gender = data.get('gender', 'male')
            speed = int(data.get('speed', 150))
            volume = int(data.get('volume', 100))
            
            # Validate settings
            if gender not in ['male', 'female']:
                gender = 'male'
            
            speed = max(80, min(300, speed))
            volume = max(0, min(100, volume))
            
            # Load current user profile
            try:
                profile_data = self.diary_manager.load_user_profile()
            except:
                profile_data = {}
            
            # Update voice settings in profile
            if 'voice_settings' not in profile_data:
                profile_data['voice_settings'] = {}
            
            profile_data['voice_settings'] = {
                'gender': gender,
                'speed': speed,
                'volume': volume,
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # Save updated profile
            success = self.diary_manager.save_user_profile(profile_data)
            
            if success:
                # Configure the audio processor with new settings
                self.audio_processor.configure_voice_settings(gender, speed, volume)
                
                return jsonify({
                    'success': True,
                    'message': 'Voice settings saved successfully',
                    'settings': profile_data['voice_settings']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to save voice settings'
                }), 500
                
        except Exception as e:
            logger.error(f"Save voice settings error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to save voice settings: {str(e)}'
            }), 500

    def get_available_voices(self):
        """Get list of available system voices"""
        try:
            voices = self.audio_processor.get_available_voices()
            
            # Also load current user voice settings
            try:
                profile_data = self.diary_manager.load_user_profile()
                current_settings = profile_data.get('voice_settings', {
                    'gender': 'male',
                    'speed': 150,
                    'volume': 100
                })
            except:
                current_settings = {
                    'gender': 'male',
                    'speed': 150,
                    'volume': 100
                }
            
            return jsonify({
                'success': True,
                'voices': voices,
                'current_settings': current_settings
            })
            
        except Exception as e:
            logger.error(f"Get available voices error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get available voices: {str(e)}',
                'voices': [],
                'current_settings': {'gender': 'male', 'speed': 150, 'volume': 100}
            }), 500
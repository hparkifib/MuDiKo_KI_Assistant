"""Easy Feedback Routes - API Endpoints für vereinfachte Feedback-Pipeline."""

import base64
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path

from app.core.exceptions import SessionNotFoundException, SessionExpiredException


def create_blueprint(service, plugin_config: dict) -> Blueprint:
    """Erstellt Blueprint mit allen Routes für Easy Feedback.
    
    Args:
        service: EasyFeedbackService instance
        plugin_config: Plugin-Konfiguration
        
    Returns:
        Blueprint: Flask Blueprint mit allen Endpoints
    """
    
    bp = Blueprint('easy_feedback', __name__, url_prefix='/api/tools/easy-feedback')
    
    @bp.route('/session', methods=['POST'])
    def create_session():
        """Erstellt eine neue Session.
        
        Returns:
            JSON Response mit Session-ID
        """
        try:
            session = service.session_service.create_session()
            return jsonify({
                'success': True,
                'sessionId': session.session_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/upload', methods=['POST'])
    def upload_file():
        """Upload einer Datei (Referenz oder Schüler).
        
        Form-Data:
            file: Die Datei
            role: 'referenz' oder 'schueler'
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Upload-Status
        """
        session_id = request.headers.get('X-Session-ID') or request.form.get('sessionId')
        
        if not session_id:
            # Erstelle neue Session
            session = service.session_service.create_session()
            session_id = session.session_id
        else:
            try:
                service.session_service.get_session(session_id)
            except (SessionNotFoundException, SessionExpiredException):
                session = service.session_service.create_session()
                session_id = session.session_id
        
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'Keine Datei im Request'
                }), 400
            
            file = request.files['file']
            role = request.form.get('role', 'referenz')
            
            if role not in ['referenz', 'schueler']:
                return jsonify({
                    'success': False,
                    'error': 'Rolle muss "referenz" oder "schueler" sein'
                }), 400
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'Keine Datei ausgewählt'
                }), 400
            
            # Lese Datei-Inhalt
            file_data = file.read()
            original_filename = secure_filename(file.filename)
            
            # Verarbeite Upload
            result = service.process_upload(
                session_id,
                role,
                file_data,
                original_filename
            )
            
            result['sessionId'] = session_id
            return jsonify(result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/record', methods=['POST'])
    def save_recording():
        """Speichert eine Browser-Aufnahme.
        
        JSON Body:
            audioData: Base64-kodierte Audio-Daten
            role: 'referenz' oder 'schueler'
            mimeType: MIME-Typ (z.B. 'audio/webm')
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Upload-Status
        """
        session_id = request.headers.get('X-Session-ID') or request.json.get('sessionId')
        
        if not session_id:
            session = service.session_service.create_session()
            session_id = session.session_id
        else:
            try:
                service.session_service.get_session(session_id)
            except (SessionNotFoundException, SessionExpiredException):
                session = service.session_service.create_session()
                session_id = session.session_id
        
        try:
            data = request.json
            
            if not data or 'audioData' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Keine Audio-Daten im Request'
                }), 400
            
            role = data.get('role', 'referenz')
            mime_type = data.get('mimeType', 'audio/webm')
            
            if role not in ['referenz', 'schueler']:
                return jsonify({
                    'success': False,
                    'error': 'Rolle muss "referenz" oder "schueler" sein'
                }), 400
            
            # Dekodiere Base64
            audio_data = base64.b64decode(data['audioData'])
            
            # Verarbeite Aufnahme
            result = service.process_recording(
                session_id,
                role,
                audio_data,
                mime_type
            )
            
            result['sessionId'] = session_id
            return jsonify(result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/convert', methods=['POST'])
    def convert_files():
        """Konvertiert Audio-Dateien zu MIDI falls nötig.
        
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Konversions-Status
        """
        session_id = request.headers.get('X-Session-ID') or request.json.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        try:
            result = service.convert_if_needed(session_id)
            return jsonify(result)
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/compare', methods=['POST'])
    def compare_files():
        """Vergleicht die MIDI-Dateien.
        
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Vergleichsergebnis
        """
        session_id = request.headers.get('X-Session-ID') or request.json.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        try:
            result = service.compare_midi_files(session_id)
            return jsonify(result)
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/generate', methods=['POST'])
    def generate_prompt():
        """Generiert den Feedback-Prompt.
        
        JSON Body:
            language: Sprache (optional, default: Deutsch)
            personalization: Personalisierungstext (optional)
            simpleLanguage: Einfache Sprache (optional, default: false)
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit System-Prompt und User-Prompt
        """
        session_id = request.headers.get('X-Session-ID') or request.json.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        try:
            data = request.json or {}
            
            language = data.get('language', 'Deutsch')
            personalization = data.get('personalization', '')
            simple_language = data.get('simpleLanguage', False)
            
            result = service.generate_feedback_prompt(
                session_id,
                language=language,
                personalization=personalization,
                use_simple_language=simple_language
            )
            
            return jsonify(result)
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/midi/<role>', methods=['GET'])
    def download_midi(role: str):
        """Download einer MIDI-Datei.
        
        Path Params:
            role: 'referenz' oder 'schueler'
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            MIDI-Datei zum Download
        """
        session_id = request.headers.get('X-Session-ID') or request.args.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        if role not in ['referenz', 'schueler']:
            return jsonify({
                'success': False,
                'error': 'Rolle muss "referenz" oder "schueler" sein'
            }), 400
        
        try:
            midi_path = service.get_midi_download_path(session_id, role)
            
            if not midi_path:
                return jsonify({
                    'success': False,
                    'error': f'Keine MIDI-Datei für {role} vorhanden'
                }), 404
            
            path = Path(midi_path)
            if not path.exists():
                return jsonify({
                    'success': False,
                    'error': 'MIDI-Datei nicht gefunden'
                }), 404
            
            return send_file(
                midi_path,
                as_attachment=True,
                download_name=f'{role}.mid',
                mimetype='audio/midi'
            )
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/status', methods=['GET'])
    def get_status():
        """Gibt den aktuellen Status der Session zurück.
        
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Session-Status
        """
        session_id = request.headers.get('X-Session-ID') or request.args.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        try:
            session = service.session_service.get_session(session_id)
            files_info = session.get_data('files_info') or {}
            midi_files = session.get_data('midi_files') or {}
            has_comparison = session.get_data('comparison_text') is not None
            
            # Build files response with audio/midi availability
            files = {}
            for role in ['referenz', 'schueler']:
                if role in files_info:
                    file_info = files_info[role]
                    files[role] = {
                        'audio': file_info.get('type') in ['audio', 'webm', 'mp3', 'wav', 'ogg'],
                        'midi': role in midi_files or file_info.get('type') in ['midi', 'mid']
                    }
            
            return jsonify({
                'success': True,
                'sessionId': session_id,
                'files': files,
                'hasReferenz': 'referenz' in files_info,
                'hasSchueler': 'schueler' in files_info,
                'referenzType': files_info.get('referenz', {}).get('type'),
                'schuelerType': files_info.get('schueler', {}).get('type'),
                'hasMidi': bool(midi_files),
                'hasComparison': has_comparison
            })
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/audio/<role>', methods=['GET'])
    def download_audio(role: str):
        """Download/Stream einer Audio-Datei.
        
        Path Params:
            role: 'referenz' oder 'schueler'
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            Audio-Datei zum Abspielen
        """
        session_id = request.headers.get('X-Session-ID') or request.args.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session-ID fehlt'
            }), 400
        
        if role not in ['referenz', 'schueler']:
            return jsonify({
                'success': False,
                'error': 'Rolle muss "referenz" oder "schueler" sein'
            }), 400
        
        try:
            session = service.session_service.get_session(session_id)
            files_info = session.get_data('files_info') or {}
            
            if role not in files_info:
                return jsonify({
                    'success': False,
                    'error': f'Keine Datei für {role} vorhanden'
                }), 404
            
            file_info = files_info[role]
            file_path = file_info.get('path')
            
            if not file_path:
                return jsonify({
                    'success': False,
                    'error': 'Dateipfad nicht gefunden'
                }), 404
            
            path = Path(file_path)
            if not path.exists():
                return jsonify({
                    'success': False,
                    'error': 'Datei nicht gefunden'
                }), 404
            
            # Determine mimetype
            ext = path.suffix.lower()
            mimetypes = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.webm': 'audio/webm',
                '.mid': 'audio/midi',
                '.midi': 'audio/midi'
            }
            mimetype = mimetypes.get(ext, 'application/octet-stream')
            
            return send_file(
                file_path,
                mimetype=mimetype
            )
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return bp

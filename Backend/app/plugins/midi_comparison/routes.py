# MIDI Comparison Routes - API Endpoints

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.core.exceptions import SessionNotFoundException, SessionExpiredException, InvalidFileFormatException


def create_routes(midi_service, session_service, storage_service) -> Blueprint:
    """Erstellt Blueprint mit allen Routes für MIDI Comparison.
    
    Args:
        midi_service: MidiComparisonService instance
        session_service: SessionService instance
        storage_service: StorageService instance
        
    Returns:
        Blueprint: Flask Blueprint mit allen Endpoints
    """
    
    bp = Blueprint('midi_comparison', __name__)
    
    @bp.route('/upload', methods=['POST'])
    def upload_midi():
        """Upload von Referenz- und Schüler-MIDI-Dateien.
        
        Form-Data:
            referenz: Referenz-MIDI-Datei
            schueler: Schüler-MIDI-Datei
            
        Headers:
            X-Session-ID: Session-ID (optional, wird automatisch erstellt falls nicht vorhanden)
            
        Returns:
            JSON Response mit Upload-Status
        """
        # Session-ID holen oder erstellen
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
        if not session_id:
            # Erstelle neue Session automatisch
            session = session_service.create_session()
            session_id = session.session_id
        else:
            try:
                # Validiere existierende Session
                session = session_service.get_session(session_id)
            except (SessionNotFoundException, SessionExpiredException):
                # Session ungültig, erstelle neue
                session = session_service.create_session()
                session_id = session.session_id
        
        try:
            
            # Lösche vorherige Dateien
            storage_service.delete_all_files(session_id)
            
            files = request.files
            
            # Validierung: Beide Dateien müssen vorhanden sein
            if "referenz" not in files or "schueler" not in files:
                return jsonify({
                    "error": "Bitte beide MIDI-Dateien hochladen (Referenz und Schüler).",
                    "success": False
                }), 400
            
            referenz_file = files["referenz"]
            schueler_file = files["schueler"]
            
            # Validierung: Dateien dürfen nicht leer sein
            if referenz_file.filename == '' or schueler_file.filename == '':
                return jsonify({
                    "error": "Eine oder beide Dateien sind leer.",
                    "success": False
                }), 400
            
            # Validierung: MIDI-Format
            allowed_extensions = {'.mid', '.midi'}
            ref_ext = '.' + referenz_file.filename.rsplit('.', 1)[1].lower() if '.' in referenz_file.filename else ''
            sch_ext = '.' + schueler_file.filename.rsplit('.', 1)[1].lower() if '.' in schueler_file.filename else ''
            
            if ref_ext not in allowed_extensions or sch_ext not in allowed_extensions:
                return jsonify({
                    "error": "Bitte nur MIDI-Dateien (.mid, .midi) hochladen.",
                    "success": False
                }), 400
            
            # Speichere Original-Dateinamen in Session
            session.set_data('original_filenames', {
                "referenz": referenz_file.filename,
                "schueler": schueler_file.filename
            })
            
            # Speichere Dateien mit Rollen
            referenz_file.filename = secure_filename(referenz_file.filename)
            schueler_file.filename = secure_filename(schueler_file.filename)
            
            referenz_path = storage_service.save_file(referenz_file, session_id, role="referenz")
            schueler_path = storage_service.save_file(schueler_file, session_id, role="schueler")
            
            # Erstelle File-Map
            file_map = {
                "referenz": referenz_path.name,
                "schueler": schueler_path.name
            }
            
            original_filenames = session.get_data('original_filenames', {})
            
            return jsonify({
                "success": True,
                "message": "MIDI-Dateien erfolgreich hochgeladen",
                "file_map": file_map,
                "original_filenames": original_filenames,
                "sessionId": session_id
            })
        
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 401
        except Exception as e:
            print(f"Fehler beim Upload: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Fehler beim Upload: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/analyze', methods=['POST'])
    def analyze_midi():
        """Analysiert und vergleicht die hochgeladenen MIDI-Dateien.
        
        JSON Body:
            referenzFile: Dateiname der Referenz-MIDI
            schuelerFile: Dateiname der Schüler-MIDI
            language: Sprache für Feedback (optional)
            personalization: Personalisierungstext (optional)
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Analyse-Ergebnis und System-Prompt
        """
        session_id = request.headers.get("X-Session-ID") or request.json.get("sessionId")
        if not session_id:
            return jsonify({
                "error": "sessionId fehlt",
                "success": False
            }), 400
        
        try:
            # Validiere Session
            session = session_service.get_session(session_id)
            
            # Hole Parameter
            data = request.json
            reference_file = data.get('referenzFile')
            student_file = data.get('schuelerFile')
            language = data.get('language', 'Deutsch')
            personalization = data.get('personalization', '')
            
            if not reference_file or not student_file:
                return jsonify({
                    "error": "Dateinamen fehlen",
                    "success": False
                }), 400
            
            # MIDI-Vergleich durchführen
            comparison_result = midi_service.compare_midi_files(
                session_id,
                reference_file,
                student_file
            )
            
            # Generiere System-Prompt
            system_prompt = midi_service.generate_feedback_prompt(
                comparison_result['comparison_text'],
                language=language,
                personalization=personalization
            )
            
            # Hole Original-Dateinamen
            original_filenames = session.get_data('original_filenames', {})
            file_map = {
                "referenz": reference_file,
                "schueler": student_file
            }
            
            return jsonify({
                "success": True,
                "system_prompt": system_prompt,
                "comparison_text": comparison_result['comparison_text'],
                "summary": comparison_result['summary'],
                "file_map": file_map,
                "original_filenames": original_filenames,
                "sessionId": session_id
            })
        
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 401
        except Exception as e:
            print(f"Fehler bei der MIDI-Analyse: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Fehler bei der Analyse: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/session/cleanup', methods=['POST'])
    def cleanup_session():
        """Beendet eine Session und löscht alle zugehörigen Daten.
        
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Cleanup-Status
        """
        session_id = request.headers.get("X-Session-ID") or request.json.get("sessionId")
        if not session_id:
            return jsonify({
                "error": "sessionId fehlt",
                "success": False
            }), 400
        
        try:
            success = session_service.end_session(session_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Session erfolgreich beendet"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Session nicht gefunden"
                }), 404
        
        except Exception as e:
            print(f"Fehler beim Session-Cleanup: {str(e)}")
            return jsonify({
                "error": f"Fehler beim Cleanup: {str(e)}",
                "success": False
            }), 500
    
    return bp

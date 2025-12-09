# Audio Feedback Routes - API Endpoints

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

from app.core.exceptions import SessionNotFoundException, SessionExpiredException, InvalidFileFormatException

def create_routes(feedback_service, session_service, storage_service, audio_service) -> Blueprint:
    """Erstellt Blueprint mit allen Routes für Audio Feedback.
    
    Args:
        feedback_service: AudioFeedbackService instance
        session_service: SessionService instance
        storage_service: StorageService instance
        audio_service: AudioService instance
        
    Returns:
        Blueprint: Flask Blueprint mit allen Endpoints
    """
    
    bp = Blueprint('audio_feedback', __name__)
    
    @bp.route('/upload', methods=['POST'])
    def upload_audio():
        """Upload von Referenz- und Schüler-Aufnahmen.
        
        Form-Data:
            referenz: Referenz-Audio-Datei
            schueler: Schüler-Audio-Datei
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Upload-Status
        """
        # Session-ID validieren
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
        if not session_id:
            return jsonify({
                "error": "sessionId fehlt",
                "success": False
            }), 400
        
        try:
            # Validiere Session
            session = session_service.get_session(session_id)
            
            # Lösche vorherige Dateien
            storage_service.delete_all_files(session_id)
            
            files = request.files
            
            # Validierung: Beide Dateien müssen vorhanden sein
            if "referenz" not in files or "schueler" not in files:
                return jsonify({
                    "error": "Bitte beide Audiodateien hochladen (Referenz und Schüler).",
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
                "message": "Dateien erfolgreich hochgeladen",
                "file_map": file_map,
                "original_filenames": original_filenames,
                "sessionId": session_id
            })
        
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 401
        except InvalidFileFormatException as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 400
        except Exception as e:
            return jsonify({
                "error": f"Fehler beim Upload: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/recordings', methods=['GET'])
    def get_recordings():
        """Gibt Informationen über hochgeladene Dateien zurück.
        
        Headers/Query:
            X-Session-ID oder sessionId: Session-ID
            
        Returns:
            JSON Response mit Datei-Informationen
        """
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
        if not session_id:
            return jsonify({
                "success": False,
                "error": "sessionId fehlt"
            }), 400
        
        try:
            # Validiere Session
            session = session_service.get_session(session_id)
            
            # Liste Dateien
            files = storage_service.list_files(session_id)
            
            # Erstelle File-Map
            file_map = {
                "referenz": "referenz.mp3" if any(f.startswith("referenz.") for f in files) else None,
                "schueler": "schueler.mp3" if any(f.startswith("schueler.") for f in files) else None
            }
            
            # Hole Original-Dateinamen
            original_filenames = session.get_data('original_filenames', {
                "referenz": "Keine Datei hochgeladen",
                "schueler": "Keine Datei hochgeladen"
            })
            
            return jsonify({
                "success": True,
                "file_map": file_map,
                "original_filenames": original_filenames,
                "files_available": len(files) > 0,
                "sessionId": session_id
            })
        
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 401
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler: {str(e)}"
            }), 500
    
    @bp.route('/analyze', methods=['POST'])
    def generate_feedback():
        """Generiert Audio-Feedback durch Analyse.
        
        JSON Body:
            language: Sprache für Feedback
            customLanguage: Benutzerdefinierte Sprache
            referenzInstrument: Instrument der Referenz
            schuelerInstrument: Instrument des Schülers
            personalMessage: Persönliche Nachricht
            prompt_type: Art des Prompts (contextual/data_only)
            use_simple_language: Einfache Sprache verwenden
            
        Headers:
            X-Session-ID: Session-ID
            
        Returns:
            JSON Response mit Analyse-Ergebnissen
        """
        # Extrahiere Parameter
        data = request.json or {}
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId") or data.get("sessionId")
        
        if not session_id:
            return jsonify({
                "error": "sessionId fehlt",
                "success": False
            }), 400
        
        try:
            # Validiere Session
            session = session_service.get_session(session_id)
            session_path = str(session.path)
            
            # Parameter extrahieren
            selected_language = data.get("language", "english")
            custom_language = data.get("customLanguage", "")
            referenz_instrument = data.get("referenzInstrument", "").strip() or "keine Angabe"
            schueler_instrument = data.get("schuelerInstrument", "").strip() or "keine Angabe"
            personal_message = data.get("personalMessage", "").strip()
            prompt_type = data.get("prompt_type", "contextual")
            use_simple_language = data.get("use_simple_language", False)
            
            # Lade und validiere Dateien
            files = storage_service.list_files(session_id)
            
            referenz_file = None
            schueler_file = None
            for f in files:
                if f.startswith("referenz."):
                    referenz_file = f
                elif f.startswith("schueler."):
                    schueler_file = f
            
            if not referenz_file or not schueler_file:
                return jsonify({
                    "error": "Eine oder beide Dateien fehlen. Bitte laden Sie die Dateien erneut hoch.",
                    "success": False
                }), 400
            
            # Zusätzliche Dateisystem-Validierung
            referenz_path = storage_service.get_file_path(session_id, referenz_file)
            schueler_path = storage_service.get_file_path(session_id, schueler_file)
            
            if not referenz_path or not schueler_path:
                return jsonify({
                    "error": "Dateien im Dateisystem nicht gefunden.",
                    "success": False
                }), 400
            
            # Segmentiere Audio-Dateien
            segment_length_sec = 8
            
            ref_segment_files = audio_service.segment_and_save(
                referenz_path,
                session.path,
                segment_length_sec,
                base_filename="referenz"
            )
            
            sch_segment_files = audio_service.segment_and_save(
                schueler_path,
                session.path,
                segment_length_sec,
                base_filename="schueler"
            )
            
            # Konvertiere Segment-Dateipfade in das erwartete Format
            # AudioFeedbackPipeline erwartet: [{"filename": str, "start_sec": float, "end_sec": float}, ...]
            ref_segments = []
            for idx, filepath in enumerate(ref_segment_files):
                ref_segments.append({
                    "filename": filepath,
                    "start_sec": idx * segment_length_sec,
                    "end_sec": (idx + 1) * segment_length_sec
                })
            
            sch_segments = []
            for idx, filepath in enumerate(sch_segment_files):
                sch_segments.append({
                    "filename": filepath,
                    "start_sec": idx * segment_length_sec,
                    "end_sec": (idx + 1) * segment_length_sec
                })
            
            # Führe Analyse durch
            result = feedback_service.analyze_recordings(
                session_id=session_id,
                session_path=session_path,
                referenz_segments=ref_segments,
                schueler_segments=sch_segments,
                language=selected_language,
                referenz_instrument=referenz_instrument,
                schueler_instrument=schueler_instrument,
                personal_message=personal_message,
                prompt_type=prompt_type,
                use_simple_language=use_simple_language
            )
            
            # Hole Original-Dateinamen
            original_filenames = session.get_data('original_filenames', {})
            
            # File-Map
            file_map = {
                "referenz": referenz_file,
                "schueler": schueler_file
            }
            
            return jsonify({
                "success": True,
                "system_prompt": result['system_prompt'],
                "analysis_data": result['analysis_data'],
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
            print(f"Fehler bei der Feedback-Generierung: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Fehler bei der Feedback-Generierung: {str(e)}",
                "success": False
            }), 500
    
    return bp

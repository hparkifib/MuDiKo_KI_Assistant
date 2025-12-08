# Flask API für Audio-Feedback-Analyse
# REST API für React Frontend zur Analyse von Musikaufnahmen

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
from werkzeug.utils import secure_filename
import threading
import os
import uuid
import shutil
import time
from AudioManager import AudioManager
from AudioFeedbackPipeline import AudioFeedbackPipeline

# Flask-App initialisieren
app = Flask(__name__)
# Sicherheit: SECRET_KEY muss in Produktion gesetzt sein
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '104857600'))  # 100 MB

# CORS konfigurieren - erlaube Anfragen vom React Frontend
# Port 5173 für lokale Vite Dev Server, Port 3000 für Docker Dev
# CORS aus ENV konfigurierbar, in Dev localhost zulassen
cors_origins = os.getenv('CORS_ORIGINS')
if cors_origins:
    origins = [o.strip() for o in cors_origins.split(',') if o.strip()]
else:
    origins = ['http://localhost:5173', 'http://localhost:3000']
CORS(app, origins=origins)

# OpenAI-Client für zukünftige Erweiterungen (aktuell nicht verwendet)
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload-Ordner Basis konfigurieren und AudioManager initialisieren
UPLOAD_FOLDER_BASE = os.path.join(app.root_path, "Uploads")
os.makedirs(UPLOAD_FOLDER_BASE, exist_ok=True)
audio_mgr = AudioManager(UPLOAD_FOLDER_BASE)
app.register_blueprint(audio_mgr.bp)  # Blueprint für Datei-Serving registrieren

# Einfache In-Memory Session-Registry
SESSIONS = {}
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))  # 1h Default

def new_session_id() -> str:
    return uuid.uuid4().hex

def session_path(session_id: str) -> str:
    # Nur hex-UUIDs erlauben
    if not session_id or not all(c in "0123456789abcdef" for c in session_id.lower()):
        raise ValueError("Ungültige Session-ID")
    return os.path.join(UPLOAD_FOLDER_BASE, session_id)

def touch_session(session_id: str):
    now = int(time.time())
    meta = SESSIONS.get(session_id, {})
    meta["lastAccess"] = now
    SESSIONS[session_id] = meta

def ensure_session_dir(session_id: str) -> str:
    base = session_path(session_id)
    os.makedirs(base, exist_ok=True)
    return base

def cleanup_session(session_id: str):
    path = session_path(session_id)
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
    SESSIONS.pop(session_id, None)

def gc_expired_sessions():
    now = int(time.time())
    expired = [sid for sid, meta in SESSIONS.items() if meta.get("lastAccess", 0) + SESSION_TTL_SECONDS < now]
    for sid in expired:
        cleanup_session(sid)

def start_gc_scheduler(interval_seconds: int = 900):
    # Einfacher Hintergrund-Thread für periodisches GC
    def _loop():
        while True:
            try:
                gc_expired_sessions()
            except Exception:
                pass
            time.sleep(interval_seconds)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()

@app.route("/api/health")
def health_check():
    """Health check endpoint für API Status."""
    return jsonify({"status": "ok", "message": "Audio Feedback API is running"})

# Upload-Validierung
ALLOWED_EXTENSIONS = {"mp3", "wav", "mp4"}
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/session/start", methods=["POST"])
def session_start():
    gc_expired_sessions()
    sid = new_session_id()
    ensure_session_dir(sid)
    touch_session(sid)
    return jsonify({"success": True, "sessionId": sid, "ttl": SESSION_TTL_SECONDS})

@app.route("/api/session/end", methods=["POST"])
def session_end():
    data = request.json or {}
    sid = data.get("sessionId") or request.args.get("sessionId")
    if not sid:
        return jsonify({"success": False, "error": "sessionId fehlt"}), 400
    try:
        cleanup_session(sid)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat-Endpoint für zukünftige OpenAI-Integration (aktuell nicht aktiv)."""
    data = request.json or {}
    msg = data.get("message", "")
    # TODO: Implement OpenAI integration
    return jsonify({"response": "Chat endpoint not yet implemented", "message": msg})

@app.route("/api/upload-audio", methods=["POST"])
def upload_audio():
    """API Endpoint für Upload von Referenz- und Schüler-Audiodateien.
    
    Erwartet zwei Dateien:
    - 'referenz': Die Lehrkraft-Aufnahme als Vergleichsstandard
    - 'schueler': Die Schüler-Aufnahme zum Vergleich
    
    Returns:
        JSON Response mit Upload-Status und Datei-Informationen
    """
    # Session-ID validieren
    session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
    # Falls keine Session-ID übergeben wurde, neue Session erstellen (Abwärtskompatibilität)
    if not session_id:
        session_id = new_session_id()
        ensure_session_dir(session_id)
        touch_session(session_id)
    try:
        base_folder = ensure_session_dir(session_id)
    except Exception:
        return jsonify({"error": "Ungültige sessionId", "success": False}), 400

    touch_session(session_id)
    # Lösche vorherige Dateien innerhalb der Session, um Speicher zu sparen
    audio_mgr.delete_all_files(base_folder)

    files = request.files
    # Validierung: Beide Dateien müssen vorhanden sein
    if "referenz" not in files or "schueler" not in files:
        return jsonify({
            "error": "Bitte beide Audiodateien hochladen (Referenz und Schüler).",
            "success": False
        }), 400

    # Extrahiere die hochgeladenen Dateien
    referenz_file = files["referenz"]
    schueler_file = files["schueler"]

    # Validierung: Dateien dürfen nicht leer sein
    if referenz_file.filename == '' or schueler_file.filename == '':
        return jsonify({
            "error": "Eine oder beide Dateien sind leer.",
            "success": False
        }), 400

    # Serverseitige Validierung von Dateiendungen
    if not (allowed_file(referenz_file.filename) and allowed_file(schueler_file.filename)):
        return jsonify({
            "error": "Nicht unterstützter Dateityp. Erlaubt sind MP3, WAV, MP4.",
            "success": False
        }), 400

    # Speichere Dateien mit standardisierten Namen (referenz.mp3, schueler.mp3)
    # Sichere Dateinamen intern verwenden (werden ohnehin standardisiert: referenz.mp3/schueler.mp3)
    referenz_file.filename = secure_filename(referenz_file.filename)
    schueler_file.filename = secure_filename(schueler_file.filename)
    referenz_name = audio_mgr.save_with_role(referenz_file, "referenz", base_folder)
    schueler_name = audio_mgr.save_with_role(schueler_file, "schueler", base_folder)

    # Behalte die ursprünglichen Dateinamen für die Anzeige
    original_filenames = {
        "referenz": referenz_file.filename,
        "schueler": schueler_file.filename
    }

    # Erstelle Mapping für Response
    file_map = audio_mgr.map_files_to_roles([referenz_name, schueler_name])

    return jsonify({
        "success": True,
        "message": "Dateien erfolgreich hochgeladen",
        "file_map": file_map,
        "original_filenames": original_filenames,
        "sessionId": session_id
    })

@app.route("/api/recordings", methods=["GET"])
def get_recordings():
    """API Endpoint zum Abrufen der Informationen über hochgeladene Dateien.
    
    Returns:
        JSON Response mit aktuellen Datei-Informationen
    """
    session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
    if not session_id:
        return jsonify({"success": False, "error": "sessionId fehlt"}), 400
    try:
        base_folder = ensure_session_dir(session_id)
    except Exception:
        return jsonify({"success": False, "error": "Ungültige sessionId"}), 400
    touch_session(session_id)
    files = audio_mgr.list_files(base_folder)
    file_map = audio_mgr.map_files_to_roles(files)
    
    # Hole die ursprünglichen Dateinamen
    original_filenames = {
        "referenz": audio_mgr.original_filenames.get("referenz", "Keine Datei hochgeladen"),
        "schueler": audio_mgr.original_filenames.get("schueler", "Keine Datei hochgeladen")
    }
    
    return jsonify({
        "success": True,
        "file_map": file_map,
        "original_filenames": original_filenames,
        "files_available": len(files) > 0,
        "sessionId": session_id
    })

def get_user_language(selected_language, custom_language):
    """Ermittelt die vom Benutzer ausgewählte Sprache."""
    if selected_language == "custom" and custom_language:
        return custom_language
    language_map = {
        "deutsch": "Deutsch",
        "english": "Englisch", 
        "español": "Spanisch",
        "français": "Französisch",
        "italiano": "Italienisch",
        "türkçe": "Türkisch"
    }
    return language_map.get(selected_language, "English")


def get_selected_topics(request):
    """Extrahiert die ausgewählten Themenfilter aus dem Formular."""
    return request.form.getlist("topics")


def create_feedback_pipeline(upload_folder):
    """Erstellt eine neue Instanz der AudioFeedbackPipeline."""
    return AudioFeedbackPipeline(
        upload_folder, 
        target_sr=22050,      # Sample Rate
        target_length=60      # Maximale Länge in Sekunden
    )

@app.route("/api/generate-feedback", methods=["POST"])
def generate_feedback():
    """API Endpoint zur Generierung des Audio-Feedbacks.
    
    Verarbeitet die hochgeladenen Audio-Dateien durch:
    1. Segmentierung in 8-Sekunden-Abschnitte
    2. Audio-Feature-Analyse (Tempo, Tonhöhe, Lautstärke, etc.)
    3. Vergleich zwischen Referenz und Schüler-Aufnahme
    4. Generierung eines strukturierten Feedback-Prompts
    
    JSON Body Parameter:
        language: Gewählte Sprache für das Feedback
        customLanguage: Benutzerdefinierte Sprache (falls 'custom' gewählt)
        referenzInstrument: Instrument der Referenzaufnahme
        schuelerInstrument: Instrument der Schüleraufnahme
        personalMessage: Persönliche Nachricht/Anweisungen für das Feedback
        prompt_type: Art des Prompts (contextual oder data_only)
        use_simple_language: Boolean für einfache Sprache
    
    Returns:
        JSON Response mit generiertem Feedback oder Fehlermeldung
    """
    # Extrahiere Benutzer-Eingaben aus dem JSON Body
    data = request.json or {}
    selected_language = data.get("language", "english")
    custom_language = data.get("customLanguage", "")
    referenz_instrument = data.get("referenzInstrument", "").strip() or "keine Angabe"
    schueler_instrument = data.get("schuelerInstrument", "").strip() or "keine Angabe"
    personal_message = data.get("personalMessage", "").strip()
    prompt_type = data.get("prompt_type", "contextual")
    use_simple_language = data.get("use_simple_language", False)

    # Session-ID validieren
    session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId") or data.get("sessionId")
    if not session_id:
        return jsonify({"error": "sessionId fehlt", "success": False}), 400
    try:
        base_folder = ensure_session_dir(session_id)
    except Exception:
        return jsonify({"error": "Ungültige sessionId", "success": False}), 400
    touch_session(session_id)

    # Lade und validiere die gespeicherten Audio-Dateien
    files = audio_mgr.list_files(base_folder)
    file_map = audio_mgr.map_files_to_roles(files)

    referenz_file = file_map.get("referenz")
    schueler_file = file_map.get("schueler")

    # Validierung: Beide Dateien müssen existieren
    if not referenz_file or not schueler_file:
        return jsonify({
            "error": "Eine oder beide Dateien fehlen. Bitte laden Sie die Dateien erneut hoch.",
            "success": False
        }), 400

    # Zusätzliche Dateisystem-Validierung
    if not os.path.exists(os.path.join(base_folder, referenz_file)) or not os.path.exists(os.path.join(base_folder, schueler_file)):
        return jsonify({
            "error": "Eine oder beide Dateien fehlen im Dateisystem. Bitte laden Sie die Dateien erneut hoch.",
            "success": False
        }), 400

    # Hole die ursprünglichen Dateinamen für die Anzeige
    original_filenames = {
        "referenz": audio_mgr.original_filenames.get("referenz", "Keine Datei hochgeladen"),
        "schueler": audio_mgr.original_filenames.get("schueler", "Keine Datei hochgeladen")
    }
    
    # Debug-Ausgaben für Entwicklung
    # Keine Original-Dateinamen im Log ausgeben (DSGVO)

    try:
        # Initialisiere die Audio-Analyse-Pipeline
        feedback_pipeline = AudioFeedbackPipeline(base_folder)

        # Segmentiere beide Audio-Dateien in 8-Sekunden-Abschnitte
        segment_length_sec = 8
        ref_segments = audio_mgr.segment_and_save(referenz_file, segment_length_sec, base_folder)
        sch_segments = audio_mgr.segment_and_save(schueler_file, segment_length_sec, base_folder)

        # Debug-Ausgaben für Segmentierung
    # Debug nur lokal: keine Segment-Dateinamen im Produktivlog

        # Führe die komplette Audio-Analyse durch und generiere Feedback
        result = feedback_pipeline.analyze_and_generate_feedback(
            ref_segments, sch_segments, selected_language, referenz_instrument, schueler_instrument, personal_message, prompt_type, use_simple_language
        )

        system_prompt = result['system_prompt']
        analysis_data = result['analysis_data']

        return jsonify({
            "success": True,
            "system_prompt": system_prompt,
            "analysis_data": analysis_data,
            "file_map": file_map,
            "original_filenames": original_filenames,
            "sessionId": session_id
        })

    except Exception as e:
        print(f"Fehler bei der Feedback-Generierung: {str(e)}")
        return jsonify({
            "error": f"Fehler bei der Feedback-Generierung: {str(e)}",
            "success": False
        }), 500


@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """API Endpoint zum Servieren hochgeladener Audio-Dateien für Wiedergabe (sessionsicher)."""
    session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
    if not session_id:
        # Fallback: wenn genau eine aktive Session den gesuchten Dateinamen hat, diese verwenden
        candidates = []
        for sid in list(SESSIONS.keys()):
            try:
                base = ensure_session_dir(sid)
                if os.path.isfile(os.path.join(base, filename)):
                    candidates.append(sid)
            except Exception:
                continue
        if len(candidates) == 1:
            session_id = candidates[0]
        else:
            return jsonify({"success": False, "error": "sessionId fehlt"}), 400
    try:
        base_folder = ensure_session_dir(session_id)
    except Exception:
        return jsonify({"success": False, "error": "Ungültige sessionId"}), 400
    try:
        return send_from_directory(base_folder, filename)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404

# Starte die Flask-Anwendung
if __name__ == "__main__":
    # Server auf allen Interfaces (0.0.0.0) und Port 5000 starten
    # Ermöglicht Zugriff von anderen Geräten im Netzwerk
    # Starte periodischen GC im Hintergrund
    try:
        start_gc_scheduler(interval_seconds=int(os.getenv('GC_INTERVAL_SECONDS', '900')))
    except Exception:
        pass
    app.run(host="0.0.0.0", port=5000)

# Flask API für Audio-Feedback-Analyse
# REST API für React Frontend zur Analyse von Musikaufnahmen

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from AudioManager import AudioManager
from AudioFeedbackPipeline import AudioFeedbackPipeline

# Flask-App initialisieren
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')

# CORS konfigurieren - erlaube Anfragen vom React Frontend
CORS(app, origins=['http://localhost:5173'])

# OpenAI-Client für zukünftige Erweiterungen (aktuell nicht verwendet)
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload-Ordner konfigurieren und AudioManager initialisieren
UPLOAD_FOLDER = os.path.join(app.root_path, "Uploads")
audio_mgr = AudioManager(UPLOAD_FOLDER)
app.register_blueprint(audio_mgr.bp)  # Blueprint für Datei-Serving registrieren

@app.route("/api/health")
def health_check():
    """Health check endpoint für API Status."""
    return jsonify({"status": "ok", "message": "Audio Feedback API is running"})

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
    # Lösche vorherige Dateien um Speicherplatz zu sparen
    audio_mgr.delete_all_files()

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

    # Speichere Dateien mit standardisierten Namen (referenz.mp3, schueler.mp3)
    referenz_name = audio_mgr.save_with_role(referenz_file, "referenz")
    schueler_name = audio_mgr.save_with_role(schueler_file, "schueler")

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
        "original_filenames": original_filenames
    })

@app.route("/api/recordings", methods=["GET"])
def get_recordings():
    """API Endpoint zum Abrufen der Informationen über hochgeladene Dateien.
    
    Returns:
        JSON Response mit aktuellen Datei-Informationen
    """
    files = audio_mgr.list_files()
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
        "files_available": len(files) > 0
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
        topics: Liste der Feedback-Schwerpunkte
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
    selected_topics = data.get("topics", [])
    prompt_type = data.get("prompt_type", "contextual")
    use_simple_language = data.get("use_simple_language", False)

    # Lade und validiere die gespeicherten Audio-Dateien
    files = audio_mgr.list_files()
    print("Dateien im Upload-Ordner:", files)  # Debug-Ausgabe
    file_map = audio_mgr.map_files_to_roles(files)
    print("Aktuelles file_map:", file_map)  # Debug-Ausgabe

    referenz_file = file_map.get("referenz")
    schueler_file = file_map.get("schueler")

    # Validierung: Beide Dateien müssen existieren
    if not referenz_file or not schueler_file:
        return jsonify({
            "error": "Eine oder beide Dateien fehlen. Bitte laden Sie die Dateien erneut hoch.",
            "success": False
        }), 400

    # Zusätzliche Dateisystem-Validierung
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, referenz_file)) or not os.path.exists(os.path.join(UPLOAD_FOLDER, schueler_file)):
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
    print("Original filenames aus AudioManager:", audio_mgr.original_filenames)
    print("Übergebene original_filenames:", original_filenames)

    try:
        # Initialisiere die Audio-Analyse-Pipeline
        feedback_pipeline = AudioFeedbackPipeline(UPLOAD_FOLDER)
        
        # Segmentiere beide Audio-Dateien in 8-Sekunden-Abschnitte
        segment_length_sec = 8
        ref_segments = audio_mgr.segment_and_save(referenz_file, segment_length_sec)
        sch_segments = audio_mgr.segment_and_save(schueler_file, segment_length_sec)
            
        # Debug-Ausgaben für Segmentierung
        print("Referenz-Segmente:", ref_segments)
        print("Schüler-Segmente:", sch_segments)
        
        # Führe die komplette Audio-Analyse durch und generiere Feedback
        result = feedback_pipeline.analyze_and_generate_feedback(
            ref_segments, sch_segments, selected_language, referenz_instrument, schueler_instrument, selected_topics, prompt_type, use_simple_language
        )
        
        feedback_prompt = result['feedback_prompt']

        return jsonify({
            "success": True,
            "feedback_prompt": feedback_prompt,
            "file_map": file_map,
            "original_filenames": original_filenames
        })

    except Exception as e:
        print(f"Fehler bei der Feedback-Generierung: {str(e)}")
        return jsonify({
            "error": f"Fehler bei der Feedback-Generierung: {str(e)}",
            "success": False
        }), 500


@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """API Endpoint zum Servieren hochgeladener Audio-Dateien für Wiedergabe."""
    return audio_mgr.serve(filename)

# Starte die Flask-Anwendung
if __name__ == "__main__":
    # Server auf allen Interfaces (0.0.0.0) und Port 5000 starten
    # Ermöglicht Zugriff von anderen Geräten im Netzwerk
    app.run(host="0.0.0.0", port=5000)

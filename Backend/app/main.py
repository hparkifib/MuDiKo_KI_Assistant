"""MuDiKo KI Assistant - Main Entry Point

Plugin-basierte Musikanalyse-Anwendung für Audio- und MIDI-Feedback.
"""

from app.core.app_factory import create_app

app = create_app()

if __name__ == "__main__":
    # Server auf allen Interfaces (0.0.0.0) und Port 5000 starten
    app.run(host="0.0.0.0", port=5000)

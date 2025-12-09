# MuDiKo KI Assistant - Main Entry Point
# Neue plugin-basierte Architektur

from app.core.app_factory import create_app

# Erstelle App mit Factory Pattern
app = create_app()

if __name__ == "__main__":
    # Server auf allen Interfaces (0.0.0.0) und Port 5000 starten
    app.run(host="0.0.0.0", port=5000)

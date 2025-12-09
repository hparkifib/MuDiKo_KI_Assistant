# Session Model - Repräsentiert eine User-Session

from datetime import datetime, timedelta
from pathlib import Path
import shutil
from typing import Optional, Dict, Any

class Session:
    """Repräsentiert eine User-Session mit Lebenszyklus."""
    
    def __init__(self, session_id: str, base_path: Path, ttl_seconds: int):
        """Initialisiert eine neue Session.
        
        Args:
            session_id: Eindeutige Session-ID
            base_path: Basis-Pfad für Session-Daten
            ttl_seconds: Time-to-Live in Sekunden
        """
        self.session_id = session_id
        self.base_path = base_path
        self.ttl_seconds = ttl_seconds
        self.created_at = datetime.now()
        self.last_access = datetime.now()
        self.data: Dict[str, Any] = {}  # Optionale Session-Daten
        
        # Erstelle Session-Ordner
        self.path = base_path / session_id
        self.path.mkdir(parents=True, exist_ok=True)
    
    def touch(self):
        """Aktualisiert den letzten Zugriffszeitpunkt."""
        self.last_access = datetime.now()
    
    def is_expired(self) -> bool:
        """Prüft ob die Session abgelaufen ist.
        
        Returns:
            bool: True wenn abgelaufen, sonst False
        """
        expires_at = self.last_access + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expires_at
    
    def cleanup(self):
        """Löscht alle Session-Daten vom Dateisystem."""
        if self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
    
    def get_file_path(self, filename: str) -> Path:
        """Gibt den Pfad zu einer Datei in der Session zurück.
        
        Args:
            filename: Name der Datei
            
        Returns:
            Path: Vollständiger Pfad zur Datei
        """
        return self.path / filename
    
    def set_data(self, key: str, value: Any):
        """Speichert einen Wert in den Session-Daten.
        
        Args:
            key: Schlüssel
            value: Wert
        """
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Holt einen Wert aus den Session-Daten.
        
        Args:
            key: Schlüssel
            default: Default-Wert wenn nicht vorhanden
            
        Returns:
            Any: Gespeicherter Wert oder Default
        """
        return self.data.get(key, default)
    
    def __repr__(self):
        return f"Session(id={self.session_id}, expired={self.is_expired()})"

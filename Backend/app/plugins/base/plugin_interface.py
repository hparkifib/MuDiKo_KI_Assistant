# Plugin Interface - Abstract Base Class für alle Tool-Plugins

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from flask import Blueprint

class MusicToolPlugin(ABC):
    """Abstract Base Class für alle Musik-Tool-Plugins.
    
    Jedes Tool-Plugin muss diese Schnittstelle implementieren.
    Dies ermöglicht einheitliche Integration in das Core-System.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Eindeutiger interner Name des Tools (URL-safe).
        
        Beispiel: 'audio-feedback', 'midi-tool'
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versionsnummer des Tools (Semantic Versioning).
        
        Beispiel: '1.0.0'
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Anzeigename für UI.
        
        Beispiel: 'Audio Feedback Analyzer'
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Kurzbeschreibung des Tools."""
        pass
    
    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]):
        """Initialisiert das Plugin mit App-Kontext.
        
        Args:
            app_context: Dictionary mit shared services:
                - 'session_service': SessionService instance
                - 'storage_service': StorageService instance
                - 'audio_service': AudioService instance
                - 'config': Config instance
        """
        pass
    
    @abstractmethod
    def get_blueprint(self) -> Blueprint:
        """Gibt Flask Blueprint mit allen Routes zurück.
        
        Returns:
            Blueprint: Flask Blueprint mit Tool-spezifischen Endpoints
        """
        pass
    
    @abstractmethod
    def get_frontend_routes(self) -> List[str]:
        """Gibt Frontend-Route-Pfade für dieses Tool zurück.
        
        Returns:
            List[str]: Liste der Frontend-Pfade
            
        Beispiel:
            ['/tools/audio-feedback/upload', '/tools/audio-feedback/analyze']
        """
        pass
    
    def get_dependencies(self) -> List[str]:
        """Gibt Plugin-Abhängigkeiten zurück (optional).
        
        Returns:
            List[str]: Liste von Plugin-Namen die benötigt werden
        """
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Gibt Config-Schema für Tool-spezifische Settings zurück (optional).
        
        Returns:
            Dict: JSON-Schema für Validierung
        """
        return {}
    
    def get_icon(self) -> Optional[str]:
        """Gibt Icon-Pfad für Tool zurück (optional).
        
        Returns:
            Optional[str]: Pfad zum Icon oder None
        """
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Prüft den Status des Plugins (optional).
        
        Returns:
            Dict: Status-Information
        """
        return {
            'status': 'ok',
            'name': self.name,
            'version': self.version
        }
    
    def cleanup(self):
        """Cleanup beim Shutdown (optional)."""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"

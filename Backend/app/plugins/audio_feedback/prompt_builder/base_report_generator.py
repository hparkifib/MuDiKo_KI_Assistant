# Base Report Generator - Interface für Musik-Analyse-Report-Varianten
# 
# Definiert das Interface für verschiedene Report-Generatoren.
# Ermöglicht Forschungs-Experimente mit unterschiedlichen Formatierungen
# und Feature-Kombinationen ohne die Core-Funktionalität zu beeinflussen.

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseReportGenerator(ABC):
    """Abstract Base Class für Musik-Analyse-Report-Generatoren.
    
    Jede Implementierung kann:
    - Unterschiedliche Formatierungen verwenden
    - Features selektiv ein-/ausschalten
    - Verschiedene Kontextualisierungen testen
    - Eigene Interpretationen hinzufügen
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisiert den Report Generator mit optionaler Config.
        
        Args:
            config: Konfiguration für Feature-Toggles und Formatierung
        """
        self.config = config or {}
        self._initialize_feature_mappings()
    
    @abstractmethod
    def _initialize_feature_mappings(self):
        """Initialisiert Feature-Namen und Kontext-Mappings.
        
        Muss von jeder Implementierung überschrieben werden.
        """
        pass
    
    @abstractmethod
    def generate_report(self, segment_results: List[Dict[str, Any]]) -> str:
        """Generiert den Musik-Analyse-Report.
        
        Args:
            segment_results: Liste der Segment-Analyse-Ergebnisse
            
        Returns:
            Formatierter Report als String
        """
        pass
    
    def _is_feature_enabled(self, feature_name: str) -> bool:
        """Prüft ob ein Feature aktiviert ist.
        
        Args:
            feature_name: Name des Features
            
        Returns:
            True wenn Feature aktiviert, sonst False
        """
        if 'enabled_features' not in self.config:
            return True  # Default: Alle Features aktiviert
        
        enabled_features = self.config.get('enabled_features')
        if enabled_features is None:
            return True  # None bedeutet alle Features aktiviert
        
        return feature_name in enabled_features
    
    def _get_format_style(self) -> str:
        """Gibt den konfigurierten Formatierungsstil zurück.
        
        Returns:
            Format-Style ('box', 'plain', 'markdown', etc.)
        """
        return self.config.get('format_style', 'plain')
    
    def _format_value(self, value: Any) -> str:
        """Formatiert Werte lesbar.
        
        Args:
            value: Zu formatierender Wert
            
        Returns:
            Formatierter String
        """
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, dict):
            return ", ".join([f"{k}={self._format_value(v)}" for k, v in value.items()])
        else:
            return str(value)

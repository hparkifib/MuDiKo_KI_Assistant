# Report Configuration - Konfiguration für Report-Generatoren
# 
# Ermöglicht granulare Kontrolle über Feature-Toggles, Formatierung
# und Report-Verhalten für Forschungs-Experimente.

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ReportConfig:
    """Konfiguration für Musik-Analyse-Report-Generatoren.
    
    Diese Klasse ermöglicht es, verschiedene Report-Varianten zu konfigurieren
    ohne Code zu ändern. Ideal für A/B-Testing und Forschungsexperimente.
    
    Attributes:
        enabled_features: Liste aktivierter Features (None = alle aktiv)
        format_style: Formatierungsstil ('box', 'plain', 'markdown', 'json')
        include_context: Pädagogische Kontexte zu Features hinzufügen
        include_interpretations: Bewertungen zu Metriken hinzufügen
        include_comparisons: Vergleichsmetriken einschließen
        verbosity_level: Detail-Level ('minimal', 'normal', 'detailed')
        show_reference_values: Referenz-Werte anzeigen
        show_student_values: Schüler-Werte anzeigen
        category_order: Reihenfolge der Kategorien
        
    Examples:
        # Minimal-Report: Nur Tempo und Pitch
        config = ReportConfig(
            enabled_features=['tempo', 'mean_pitch'],
            format_style='plain',
            verbosity_level='minimal'
        )
        
        # Detaillierter Report mit allem
        config = ReportConfig(
            format_style='box',
            include_context=True,
            include_interpretations=True,
            verbosity_level='detailed'
        )
        
        # Nur Feature-Extraktion ohne Kontext
        config = ReportConfig(
            format_style='plain',
            include_context=False,
            include_interpretations=False
        )
    """
    
    # Feature-Kontrolle
    enabled_features: Optional[List[str]] = None  # None = alle Features aktiv
    
    # Formatierung
    format_style: str = 'box'  # 'box', 'plain', 'markdown', 'json'
    
    # Kontext und Interpretationen
    include_context: bool = True  # Pädagogische Erklärungen
    include_interpretations: bool = True  # Bewertungen wie "Sehr ähnlich ✓"
    include_comparisons: bool = True  # Vergleichsmetriken
    
    # Detail-Level
    verbosity_level: str = 'normal'  # 'minimal', 'normal', 'detailed'
    
    # Werte-Anzeige
    show_reference_values: bool = True
    show_student_values: bool = True
    
    # Kategorien
    category_order: List[str] = field(default_factory=lambda: [
        'tempo_rhythm',
        'pitch_harmony', 
        'dynamics',
        'timbre',
        'comparison'
    ])
    
    # Zusätzliche Optionen
    custom_feature_names: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def detailed_report(cls) -> 'ReportConfig':
        """Erstellt Config für detaillierten, pädagogischen Report.
        
        - Alle Features aktiviert
        - Box-Formatierung
        - Kontext und Interpretationen
        - Detailliertes Verbosity-Level
        
        Returns:
            ReportConfig für detaillierten Report
        """
        return cls(
            format_style='box',
            include_context=True,
            include_interpretations=True,
            include_comparisons=True,
            verbosity_level='detailed'
        )
    
    @classmethod
    def technical_report(cls) -> 'ReportConfig':
        """Erstellt Config für technischen Feature-Extraktion-Report.
        
        - Alle Features aktiviert
        - Plain-Formatierung (keine Boxen)
        - Keine Kontexte oder Interpretationen
        - Nur rohe Daten
        
        Returns:
            ReportConfig für technischen Report
        """
        return cls(
            format_style='plain',
            include_context=False,
            include_interpretations=False,
            verbosity_level='normal'
        )
    
    @classmethod
    def minimal_report(cls, features: List[str]) -> 'ReportConfig':
        """Erstellt Config für minimalen Report mit ausgewählten Features.
        
        Args:
            features: Liste der zu aktivierenden Features
            
        Returns:
            ReportConfig für minimalen Report
        """
        return cls(
            enabled_features=features,
            format_style='plain',
            include_context=False,
            include_interpretations=False,
            verbosity_level='minimal'
        )
    
    @classmethod
    def experimental(cls, **kwargs) -> 'ReportConfig':
        """Erstellt Config für Experimente mit Custom-Einstellungen.
        
        Args:
            **kwargs: Beliebige Config-Parameter
            
        Returns:
            ReportConfig mit Custom-Einstellungen
        """
        return cls(**kwargs)


# Vordefinierte Feature-Sets für schnelle Experimente
FEATURE_SETS = {
    'tempo_only': ['tempo', 'onset_count', 'rhythm_std_interval', 'rhythm_mean_interval'],
    'pitch_only': ['mean_pitch', 'estimated_key', 'dominant_chord', 'vibrato_strength'],
    'dynamics_only': ['mean_rms', 'dynamic_range_db', 'num_silences', 'mean_attack_time'],
    'timbre_only': ['mean_centroid', 'timbre_variance'],
    'comparison_only': ['mfcc_distance', 'chroma_similarity', 'dtw_distance', 'rms_correlation', 'pitch_contour_correlation'],
    'minimal_core': ['tempo', 'mean_pitch', 'mean_rms'],
    'rhythm_focus': ['tempo', 'onset_count', 'rhythm_std_interval', 'dtw_distance'],
    'pitch_focus': ['mean_pitch', 'estimated_key', 'vibrato_strength', 'pitch_contour_correlation'],
}

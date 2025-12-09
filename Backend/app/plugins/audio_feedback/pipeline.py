# Audio Feedback Pipeline - Modulare Orchestrierung der Analyse-Komponenten
# 
# Diese Pipeline koordiniert die modularen Analyzer und Comparators und
# folgt dem Dependency Injection und Composition-over-Inheritance Prinzip.

import os
import librosa
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

# Import Analyzers
from .analyzers import (
    TempoAnalyzer,
    PitchAnalyzer,
    SpectralAnalyzer,
    DynamicsAnalyzer,
    TimbreAnalyzer,
    RhythmAnalyzer
)

# Import Comparators
from .comparators import (
    FeatureComparator,
    TemporalComparator,
    EnergyComparator
)

# Import Prompt Builder
from .prompt_builder import PromptGenerator
from .prompt_builder.report_config import ReportConfig

class AudioFeedbackPipeline:
    """Modulare Pipeline für Audio-Analyse und Feedback-Generierung.
    
    Diese Klasse orchestriert verschiedene spezialisierte Analyzer und Comparators,
    anstatt alle Funktionalität selbst zu implementieren (Separation of Concerns).
    """
    
    def __init__(
        self, 
        upload_folder: str, 
        target_sr: int = 22050, 
        target_length: int = 30,
        report_variant: str = 'detailed',
        report_config: Dict[str, Any] = None
    ):
        """Initialisiert die Pipeline mit allen Komponenten.
        
        Args:
            upload_folder: Pfad zum Upload-Ordner
            target_sr: Ziel-Sample-Rate
            target_length: Maximale Audio-Länge in Sekunden
            report_variant: Report-Variante ('detailed', 'technical', 'selective')
            report_config: Optionale Config für Report-Generator
        """
        self.upload_folder = upload_folder
        self.target_sr = target_sr
        self.target_length = target_length
        self.preprocessed_data = {}  # Cache
        
        # Report-Generator Config
        self.report_variant = report_variant
        self.report_config = report_config
        
        # Initialisiere Analyzers (Dependency Injection)
        self.analyzers = {
            'tempo': TempoAnalyzer(target_sr),
            'pitch': PitchAnalyzer(target_sr),
            'spectral': SpectralAnalyzer(target_sr),
            'dynamics': DynamicsAnalyzer(target_sr),
            'timbre': TimbreAnalyzer(target_sr),
            'rhythm': RhythmAnalyzer(target_sr)
        }
        
        # Initialisiere Comparators
        self.comparators = {
            'feature': FeatureComparator(),
            'temporal': TemporalComparator(),
            'energy': EnergyComparator()
        }
        
        # Initialisiere Prompt Generator mit Config
        config_obj = ReportConfig(**self.report_config) if self.report_config else None
        self.prompt_generator = PromptGenerator(
            report_variant=self.report_variant,
            report_config=config_obj
        )
    
    def preprocess_audio(self, filename: str) -> Tuple[np.ndarray, int]:
        """Lädt eine Audio-Datei.
        
        Args:
            filename: Dateiname
            
        Returns:
            Tuple von (audio_array, sample_rate)
        """
        # Suche im Upload-Ordner
        path = os.path.join(self.upload_folder, filename)
        
        # Falls nicht gefunden, im segments Unterordner suchen
        if not os.path.exists(path):
            segments_path = os.path.join(self.upload_folder, "segments", filename)
            if os.path.exists(segments_path):
                path = segments_path
            else:
                raise FileNotFoundError(f"Datei nicht gefunden: {filename}")
        
        y, sr = librosa.load(path, sr=self.target_sr)
        return y, sr
    
    def analyze_all(self, referenz_fn: str, schueler_fn: str) -> Dict[str, Any]:
        """Führt vollständige Analyse durch.
        
        Args:
            referenz_fn: Referenz-Dateiname
            schueler_fn: Schüler-Dateiname
            
        Returns:
            Dict mit allen Analyse-Ergebnissen
        """
        # Lade Audio-Daten
        ref_data = self.preprocess_audio(referenz_fn)
        sch_data = self.preprocess_audio(schueler_fn)
        
        results = {}
        
        # 1. Feature-Extraktion für beide Dateien
        for prefix, audio_data in [('referenz', ref_data), ('schueler', sch_data)]:
            for analyzer_name, analyzer in self.analyzers.items():
                features = analyzer.analyze(audio_data)
                for feature_name, feature_value in features.items():
                    results[f"{prefix}_{feature_name}"] = feature_value
        
        # 2. Vergleichsanalysen
        for comparator_name, comparator in self.comparators.items():
            comparison = comparator.compare(ref_data, sch_data)
            results.update(comparison)
        
        return results
    
    def analyze_segments(self, ref_segments: List[Dict], sch_segments: List[Dict]) -> List[Dict]:
        """Analysiert Segment-Paare.
        
        Args:
            ref_segments: Referenz-Segmente mit filename, start_sec, end_sec
            sch_segments: Schüler-Segmente mit filename, start_sec, end_sec
            
        Returns:
            Liste von Analyse-Ergebnissen pro Segment
        """
        segment_results = []
        max_segments = max(len(ref_segments), len(sch_segments))
        
        for i in range(max_segments):
            ref_seg = ref_segments[i] if i < len(ref_segments) else None
            sch_seg = sch_segments[i] if i < len(sch_segments) else None
            
            if ref_seg and sch_seg:
                # Analysiere Segment-Paar
                analysis = self.analyze_all(ref_seg["filename"], sch_seg["filename"])
                
                segment_results.append({
                    "segment": i + 1,
                    "referenz_start": ref_seg["start_sec"],
                    "referenz_end": ref_seg["end_sec"],
                    "schueler_start": sch_seg["start_sec"],
                    "schueler_end": sch_seg["end_sec"],
                    "analysis": analysis
                })
        
        return segment_results
    
    def analyze_and_generate_feedback(
        self,
        ref_segments: List[Dict],
        sch_segments: List[Dict],
        language: str,
        referenz_instrument: str,
        schueler_instrument: str,
        personal_message: str,
        prompt_type: str = "contextual",
        use_simple_language: bool = False
    ) -> Dict[str, Any]:
        """Hauptfunktion: Analysiert und generiert Feedback.
        
        Args:
            ref_segments: Referenz-Segmente
            sch_segments: Schüler-Segmente
            language: Sprache
            referenz_instrument: Referenz-Instrument
            schueler_instrument: Schüler-Instrument
            personal_message: Persönliche Nachricht
            prompt_type: Prompt-Typ
            use_simple_language: Einfache Sprache
            
        Returns:
            Dict mit system_prompt und analysis_data
        """
        # 1. Führe Segment-Analyse durch
        segment_results = self.analyze_segments(ref_segments, sch_segments)
        
        # 2. Generiere Feedback-Prompt
        result = self.prompt_generator.generate_feedback_prompt(
            segment_results,
            language,
            referenz_instrument,
            schueler_instrument,
            personal_message,
            prompt_type,
            use_simple_language
        )
        
        return result

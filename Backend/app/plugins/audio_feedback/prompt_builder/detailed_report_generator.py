# Detailed Report Generator - Detaillierter, pädagogischer Musik-Analyse-Report
# 
# Diese Variante entspricht dem aktuellen Report mit:
# - Box-Formatierung für bessere Lesbarkeit
# - Pädagogischen Kontexten zu jedem Feature
# - Interpretationen der Vergleichsmetriken
# - Kategorisierung nach musikalischen Aspekten

from typing import Dict, Any, List
from .base_report_generator import BaseReportGenerator

class DetailedReportGenerator(BaseReportGenerator):
    """Generiert detaillierte, pädagogisch optimierte Musik-Analyse-Reports.
    
    Dieser Report ist für LLM-basiertes pädagogisches Feedback optimiert und
    bietet maximalen Kontext für die Bewertung der Schülerleistung.
    
    Features:
    - Box-Formatierung mit Unicode-Zeichen (┌─, │, ═)
    - Pädagogische Feature-Namen statt technischer Begriffe
    - Referenz- und Schüler-Werte nebeneinander
    - Interpretationen der Vergleichsmetriken
    - Kategorisierung nach musikalischen Aspekten
    """
    
    def _initialize_feature_mappings(self):
        """Initialisiert pädagogische Feature-Namen (vollständig auf Deutsch)."""
        self.feature_contexts = {
            # Tempo & Rhythmus
            'tempo': 'Tempo (BPM)',
            'onset_count': 'Anzahl Noten',
            'rhythm_std_interval': 'Rhythmus-Gleichmäßigkeit',
            'rhythm_mean_interval': 'Durchschnittl. Notenabstand',
            
            # Tonhöhe & Harmonie
            'mean_pitch': 'Durchschnittliche Tonhöhe',
            'min_pitch': 'Tiefste Tonhöhe',
            'max_pitch': 'Höchste Tonhöhe',
            'estimated_key': 'Tonart',
            'dominant_chord': 'Hauptakkord',
            'chord_variety': 'Akkordvielfalt',
            'vibrato_strength': 'Vibrato-Intensität',
            'vibrato_rate': 'Vibrato-Geschwindigkeit',
            
            # Lautstärke & Dynamik
            'mean_rms': 'Durchschnittliche Lautstärke',
            'max_rms': 'Maximale Lautstärke',
            'min_rms': 'Minimale Lautstärke',
            'dynamic_range_db': 'Dynamikumfang (dB)',
            'dynamic_std_db': 'Dynamik-Schwankung (dB)',
            'num_silences': 'Anzahl Pausen',
            'total_silence_duration': 'Gesamte Pausendauer',
            'longest_silence': 'Längste Pause',
            'mean_attack_time': 'Durchschn. Anschlagszeit',
            'min_attack_time': 'Kürzeste Anschlagszeit',
            'max_attack_time': 'Längste Anschlagszeit',
            
            # Klangfarbe (Spektral)
            'mean_centroid': 'Klangfarbe (Helligkeit)',
            'min_centroid': 'Dunkelster Klang',
            'max_centroid': 'Hellster Klang',
            'mean_bandwidth': 'Klangbreite',
            'min_bandwidth': 'Minimale Klangbreite',
            'max_bandwidth': 'Maximale Klangbreite',
            'mean_rolloff': 'Spektraler Rolloff',
            'min_rolloff': 'Minimaler Rolloff',
            'max_rolloff': 'Maximaler Rolloff',
            'mean_zcr': 'Zero-Crossing-Rate',
            'min_zcr': 'Minimale ZCR',
            'max_zcr': 'Maximale ZCR',
            'timbre_variance': 'Klangfarben-Konsistenz',
            'timbre_frame_distance': 'Klangfarben-Variation',
            
            # MFCC (Timbre Details)
            'mfcc_mean_1': 'MFCC 1 (Mittelwert)',
            'mfcc_mean_2': 'MFCC 2 (Mittelwert)',
            'mfcc_mean_3': 'MFCC 3 (Mittelwert)',
            'mfcc_var_1': 'MFCC 1 (Varianz)',
            'mfcc_var_2': 'MFCC 2 (Varianz)',
            'mfcc_var_3': 'MFCC 3 (Varianz)',
            
            # Polyphonie
            'polyphony_active_bands': 'Aktive Frequenzbänder',
            'polyphony_spectral_flatness': 'Spektrale Gleichmäßigkeit',
            
            # Vergleichsmetriken
            'mfcc_distance': 'Klangfarben-Ähnlichkeit',
            'chroma_similarity': 'Harmonische Ähnlichkeit',
            'dtw_distance': 'Zeitliche Synchronität',
            'rms_correlation': 'Dynamik-Ähnlichkeit',
            'pitch_contour_correlation': 'Melodie-Ähnlichkeit',
            'energy_envelope_correlation': 'Energie-Korrelation'
        }
    
    def generate_report(self, segment_results: List[Dict[str, Any]]) -> str:
        """Generiert detaillierten Musik-Analyse-Report.
        
        Args:
            segment_results: Liste der Segment-Analyse-Ergebnisse
            
        Returns:
            Formatierter Report mit Box-Design
        """
        lines = ["\n" + "="*70]
        lines.append("MUSIK-ANALYSE-REPORT (DETAILLIERT)")
        lines.append("="*70 + "\n")
        
        for idx, segment in enumerate(segment_results, 1):
            lines.append(f"\n{'─'*70}")
            lines.append(f"Segment {idx}  |  Zeit: {segment['schueler_start']:.1f}s - {segment['schueler_end']:.1f}s")
            lines.append('─'*70 + "\n")
            
            analysis = segment.get('analysis', {})
            
            # Gruppiere Features nach Kategorien
            tempo_features = self._extract_category_features(analysis, ['tempo', 'onset_count', 'rhythm'])
            pitch_features = self._extract_category_features(analysis, ['pitch', 'key', 'chord', 'vibrato'])
            dynamics_features = self._extract_category_features(analysis, ['rms', 'dynamic', 'silence', 'attack'])
            timbre_features = self._extract_category_features(analysis, ['centroid', 'bandwidth', 'timbre', 'mfcc'])
            comparison_features = self._extract_comparison_features(analysis)
            
            # Formatiere jede Kategorie
            if tempo_features and self._is_category_enabled('tempo_rhythm'):
                lines.append("┌─ TEMPO & RHYTHMUS")
                lines.extend(self._format_features_with_context(tempo_features))
                lines.append("")
            
            if pitch_features and self._is_category_enabled('pitch_harmony'):
                lines.append("┌─ TONHÖHE & HARMONIE")
                lines.extend(self._format_features_with_context(pitch_features))
                lines.append("")
            
            if dynamics_features and self._is_category_enabled('dynamics'):
                lines.append("┌─ LAUTSTÄRKE & AUSDRUCK")
                lines.extend(self._format_features_with_context(dynamics_features))
                lines.append("")
            
            if timbre_features and self._is_category_enabled('timbre'):
                lines.append("┌─ KLANGFARBE")
                lines.extend(self._format_features_with_context(timbre_features))
                lines.append("")
            
            if comparison_features and self.config.get('include_comparisons', True):
                lines.append("┌─ VERGLEICH REFERENZ ↔ SCHÜLER")
                lines.extend(self._format_comparison_with_interpretation(comparison_features))
                lines.append("")
        
        lines.append("="*70)
        return "\n".join(lines)
    
    def _is_category_enabled(self, category: str) -> bool:
        """Prüft ob eine Kategorie aktiviert ist."""
        category_order = self.config.get('category_order', [])
        if not category_order:
            return True
        return category in category_order
    
    def _extract_category_features(self, analysis: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Extrahiert Features einer Kategorie."""
        features = {}
        for key, value in analysis.items():
            if any(keyword in key.lower() for keyword in keywords):
                # Prüfe ob Feature aktiviert ist
                clean_key = key.replace('referenz_', '').replace('schueler_', '')
                if self._is_feature_enabled(clean_key):
                    features[key] = value
        return features
    
    def _extract_comparison_features(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Vergleichs-Metriken."""
        comparison_keys = ['distance', 'similarity', 'correlation']
        features = {}
        for key, value in analysis.items():
            if any(comp_key in key.lower() for comp_key in comparison_keys):
                if self._is_feature_enabled(key):
                    features[key] = value
        return features
    
    def _format_features_with_context(self, features: Dict[str, Any]) -> List[str]:
        """Formatiert Features mit pädagogischem Kontext."""
        lines = []
        
        # Sammle Referenz- und Schüler-Werte zusammen
        paired_features = {}
        standalone_features = {}
        
        for key, value in features.items():
            if key.startswith('referenz_'):
                clean_key = key.replace('referenz_', '')
                if clean_key not in paired_features:
                    paired_features[clean_key] = {}
                paired_features[clean_key]['referenz'] = value
            elif key.startswith('schueler_'):
                clean_key = key.replace('schueler_', '')
                if clean_key not in paired_features:
                    paired_features[clean_key] = {}
                paired_features[clean_key]['schueler'] = value
            else:
                standalone_features[key] = value
        
        # Formatiere gepaarte Features (Referenz + Schüler nebeneinander)
        for feature_name, values in paired_features.items():
            display_name = self.feature_contexts.get(feature_name, feature_name)
            ref_val = values.get('referenz', 'N/A')
            sch_val = values.get('schueler', 'N/A')
            
            ref_formatted = self._format_value(ref_val)
            sch_formatted = self._format_value(sch_val)
            
            lines.append(f"│  {display_name}:")
            
            if self.config.get('show_reference_values', True):
                lines.append(f"│      Referenz:\t{ref_formatted}")
            if self.config.get('show_student_values', True):
                lines.append(f"│      Schüler:\t\t{sch_formatted}")
            
            lines.append("│")
        
        # Formatiere standalone Features
        for key, value in standalone_features.items():
            display_name = self.feature_contexts.get(key, key)
            formatted_val = self._format_value(value)
            lines.append(f"│  {display_name}:\t{formatted_val}")
            lines.append("│")
        
        return lines
    
    def _format_comparison_with_interpretation(self, features: Dict[str, Any]) -> List[str]:
        """Formatiert Vergleichsmetriken mit Interpretation."""
        lines = []
        for key, value in features.items():
            if value is None:
                continue
            
            display_name = self.feature_contexts.get(key, key)
            formatted_val = self._format_value(value)
            
            lines.append(f"│  {display_name}:")
            lines.append(f"│      Wert:\t\t{formatted_val}")
            lines.append("│")
        
        return lines
    
    def _interpret_metric(self, metric_name: str, value: float) -> str:
        """Interpretiert Vergleichsmetriken pädagogisch."""
        if 'distance' in metric_name.lower():
            if value < 5:
                return "Sehr ähnlich ✓"
            elif value < 15:
                return "Ähnlich, kleine Unterschiede"
            else:
                return "Deutliche Unterschiede"
        
        elif 'similarity' in metric_name.lower() or 'correlation' in metric_name.lower():
            if value > 0.8:
                return "Sehr gut übereinstimmend ✓"
            elif value > 0.5:
                return "Teilweise übereinstimmend"
            elif value > 0:
                return "Geringe Übereinstimmung"
            else:
                return "Wenig Übereinstimmung"
        
        return ""

"""
Conversion Parameter Optimizer - Analysiert Audio und optimiert MIDI-Konvertierungsparameter.

Nutzt die Audio-Analyzer aus dem audio_feedback Plugin, um die Referenz-MP3 zu analysieren
und die Basic Pitch Parameter dynamisch an das jeweilige Stück anzupassen.

Kann in zwei Modi arbeiten:
1. Mit Preset: Preset-Parameter werden als Basis verwendet und verfeinert
2. Ohne Preset: Alle Parameter werden komplett aus der Audio-Analyse abgeleitet
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np

from app.plugins.audio_feedback.analyzers.tempo_analyzer import TempoAnalyzer
from app.plugins.audio_feedback.analyzers.pitch_analyzer import PitchAnalyzer
from app.plugins.audio_feedback.analyzers.rhythm_analyzer import RhythmAnalyzer
from app.shared.services.audio_service import AudioService
from app.core.exceptions import AudioAnalysisError


# Basis-Tempo für die Skalierung (120 BPM als Referenz)
BASE_TEMPO = 120.0

# Minimale und maximale Werte für Parameter (Sicherheitsgrenzen)
PARAM_BOUNDS = {
    'onset_threshold': (0.3, 0.8),
    'frame_threshold': (0.3, 0.7),
    'minimum_note_length': (50, 300),  # in Millisekunden
    'minimum_frequency': (20, 500),
    'maximum_frequency': (1000, 16000),  # Erhöht für hohe Instrumente (Flöte, Violine, etc.)
}

# Standard-Defaults wenn kein Preset verwendet wird
# Diese werden dann von der Analyse überschrieben
DEFAULT_PARAMS = {
    'onset_threshold': 0.5,
    'frame_threshold': 0.4,
    'minimum_note_length': 127,  # wird durch Tempo angepasst
    'minimum_frequency': 27.5,   # wird durch Pitch-Analyse angepasst
    'maximum_frequency': 4186,   # wird durch Pitch-Analyse angepasst
    'melodia_trick': False,      # wird durch Polyphonie-Analyse angepasst
}


class ConversionParameterOptimizer:
    """Optimiert MIDI-Konvertierungsparameter basierend auf Audio-Analyse.
    
    Analysiert die Referenz-MP3 (Lehrer-Aufnahme) und passt die Parameter
    für die MIDI-Konvertierung entsprechend an. Beide Dateien (Referenz + Schüler)
    werden dann mit identischen, stück-spezifischen Parametern konvertiert.
    
    Kann mit oder ohne Preset arbeiten:
    - Mit Preset: Preset als Basis, Analyse verfeinert
    - Ohne Preset: Alle Parameter komplett aus Analyse abgeleitet
    
    Wiederverwendet die Audio-Analyzer aus dem audio_feedback Plugin.
    """
    
    def __init__(self, audio_service: AudioService):
        """Initialisiert den Optimizer.
        
        Args:
            audio_service: AudioService für Audio-Laden
        """
        self.audio_service = audio_service
        
        # Initialisiere die Analyzer (aus audio_feedback Plugin)
        self.tempo_analyzer = TempoAnalyzer()
        self.pitch_analyzer = PitchAnalyzer()
        self.rhythm_analyzer = RhythmAnalyzer()
        
        logging.debug("🔧 ConversionParameterOptimizer initialisiert")
    
    def optimize(
        self, 
        audio_path: Path,
        preset_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analysiert die Referenz-MP3 und berechnet optimale Parameter.
        
        Args:
            audio_path: Pfad zur Referenz-MP3 (Lehrer-Aufnahme)
            preset_params: Optional - Basis-Parameter aus Preset. 
                          Wenn None, werden alle Parameter aus Analyse berechnet.
            
        Returns:
            Dict mit optimierten Parametern
            
        Raises:
            AudioAnalysisError: Wenn die Audio-Analyse fehlschlägt
        """
        use_preset = preset_params is not None
        mode = "Preset-Modus" if use_preset else "Auto-Modus"
        logging.info(f"🎵 Analysiere Referenz ({mode}): {audio_path.name}")
        
        # Lade Audio
        try:
            audio_data = self.audio_service.load_audio(audio_path)
        except Exception as e:
            raise AudioAnalysisError(
                f"Audio konnte nicht geladen werden: {audio_path.name}. "
                f"Bitte prüfe das Dateiformat. Details: {e}"
            )
        
        # Führe Analysen durch
        analysis = self._analyze_audio(audio_data)
        
        # Debug: Zeige erkannte Pitch-Werte
        logging.info(
            f"📊 Analyse-Ergebnis: Tempo={analysis.get('tempo', 0):.0f} BPM, "
            f"Pitch={analysis.get('min_pitch', 0):.0f}-{analysis.get('max_pitch', 0):.0f} Hz, "
            f"Intervall={analysis.get('rhythm_mean_interval', 0):.2f}s"
        )
        
        # Berechne Parameter
        if use_preset:
            # Preset als Basis, Analyse verfeinert
            optimized_params = self._optimize_with_preset(preset_params, analysis)
        else:
            # Alle Parameter komplett aus Analyse
            optimized_params = self._calculate_from_analysis(analysis)
        
        logging.info(
            f"✅ Parameter berechnet: Tempo={analysis.get('tempo', 0):.0f} BPM, "
            f"min_note={optimized_params.get('minimum_note_length', '?')}ms, "
            f"onset={optimized_params.get('onset_threshold', '?')}, "
            f"freq={optimized_params.get('minimum_frequency', '?'):.0f}-"
            f"{optimized_params.get('maximum_frequency', '?'):.0f}Hz"
        )
        
        return optimized_params
    
    def _analyze_audio(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Führt alle relevanten Audio-Analysen durch.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit allen Analyse-Ergebnissen
            
        Raises:
            AudioAnalysisError: Wenn eine Analyse fehlschlägt
        """
        analysis = {}
        errors = []
        
        # Tempo-Analyse (BPM, Onset-Count, Rhythmus-Stabilität)
        try:
            tempo_results = self.tempo_analyzer.analyze(audio_data)
            analysis.update(tempo_results)
        except Exception as e:
            errors.append(f"Tempo-Analyse: {e}")
        
        # Pitch-Analyse (Frequenzbereich, Tonart)
        try:
            pitch_results = self.pitch_analyzer.analyze(audio_data)
            analysis.update(pitch_results)
        except Exception as e:
            errors.append(f"Pitch-Analyse: {e}")
        
        # Rhythmus/Polyphonie-Analyse
        try:
            rhythm_results = self.rhythm_analyzer.analyze(audio_data)
            analysis.update(rhythm_results)
        except Exception as e:
            errors.append(f"Rhythmus-Analyse: {e}")
        
        # Wenn alle Analysen fehlgeschlagen sind, abbrechen
        if len(errors) == 3:
            raise AudioAnalysisError(
                f"Audio-Analyse vollständig fehlgeschlagen. "
                f"Fehler: {'; '.join(errors)}"
            )
        
        # Mindestens Tempo muss vorhanden sein
        if 'tempo' not in analysis:
            raise AudioAnalysisError(
                "Tempo konnte nicht erkannt werden. "
                "Die Audio-Datei ist möglicherweise beschädigt oder enthält keine Musik."
            )
        
        return analysis
    
    def _optimize_with_preset(
        self, 
        preset_params: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimiert Preset-Parameter basierend auf der Audio-Analyse.
        
        Preset-Parameter werden als Basis verwendet und nur verfeinert,
        nicht komplett ersetzt.
        
        Args:
            preset_params: Basis-Parameter aus dem Preset
            analysis: Ergebnisse der Audio-Analyse
            
        Returns:
            Dict mit optimierten Parametern
        """
        # Kopiere Preset-Parameter als Basis
        params = dict(preset_params)
        
        # 1. Tempo-basierte Anpassung der minimalen Notenlänge
        tempo = analysis.get('tempo', BASE_TEMPO)
        params = self._adjust_for_tempo(params, tempo)
        
        # 2. Frequenzbereich anpassen (nur einengen, nicht erweitern)
        min_pitch = analysis.get('min_pitch', 0)
        max_pitch = analysis.get('max_pitch', 0)
        if min_pitch > 0 and max_pitch > 0:
            params = self._adjust_frequency_range(params, min_pitch, max_pitch)
        
        # 3. Polyphonie-basierte Anpassung von melodia_trick
        polyphony = analysis.get('polyphony_spectral_flatness', 0.5)
        params = self._adjust_for_polyphony(params, polyphony)
        
        # 4. Onset-Dichte anpassen
        mean_interval = analysis.get('rhythm_mean_interval', 0.5)
        params = self._adjust_for_density(params, mean_interval)
        
        return params
    
    def _calculate_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet alle Parameter komplett aus der Audio-Analyse.
        
        Wird verwendet wenn kein Preset angegeben wurde.
        Alle Parameter werden direkt aus den Analysedaten abgeleitet.
        
        Args:
            analysis: Ergebnisse der Audio-Analyse
            
        Returns:
            Dict mit berechneten Parametern
        """
        params = {}
        
        # === 1. TEMPO → minimum_note_length ===
        tempo = analysis.get('tempo', BASE_TEMPO)
        # Bei schnellem Tempo (>140 BPM) kürzere Noten erlauben
        # Bei langsamen Tempo (<80 BPM) längere Mindestdauer
        if tempo > 140:
            base_note_length = 80  # Schnell: kurze Noten
        elif tempo > 100:
            base_note_length = 120  # Mittel
        else:
            base_note_length = 180  # Langsam: längere Noten
        
        # Zusätzliche Skalierung
        tempo_factor = BASE_TEMPO / max(tempo, 40)
        min_note_length = base_note_length * tempo_factor
        params['minimum_note_length'] = int(self._clamp(min_note_length, *PARAM_BOUNDS['minimum_note_length']))
        
        # === 2. PITCH → Frequenzbereich ===
        min_pitch = analysis.get('min_pitch', 0)
        max_pitch = analysis.get('max_pitch', 0)
        
        # Mindest-Maximum: Garantiere dass hohe Töne nicht abgeschnitten werden
        # Klavier geht bis C8 (4186 Hz), Amélie hat Töne bis ~1400 Hz
        MIN_MAX_FREQUENCY = 3000  # Mindestens bis hier erlauben
        
        if min_pitch > 0 and max_pitch > 0:
            # Puffer hinzufügen (30% nach unten, 50% nach oben)
            calculated_min = min_pitch * 0.7
            calculated_max = max_pitch * 1.5
            
            # Stelle sicher, dass max nicht zu niedrig ist
            calculated_max = max(calculated_max, MIN_MAX_FREQUENCY)
            
            params['minimum_frequency'] = self._clamp(calculated_min, *PARAM_BOUNDS['minimum_frequency'])
            params['maximum_frequency'] = self._clamp(calculated_max, *PARAM_BOUNDS['maximum_frequency'])
        else:
            # Fallback: sehr breiter Bereich (volle Klaviatur)
            params['minimum_frequency'] = 27.5   # A0
            params['maximum_frequency'] = 4186   # C8
        
        # === 3. NOTENDICHTE → onset_threshold + frame_threshold ===
        mean_interval = analysis.get('rhythm_mean_interval', 0.5)
        
        if mean_interval < 0.15:
            # Sehr schnell: niedrigere Schwellenwerte für schnelle Noten
            params['onset_threshold'] = 0.35
            params['frame_threshold'] = 0.30
        elif mean_interval < 0.25:
            # Schnell
            params['onset_threshold'] = 0.45
            params['frame_threshold'] = 0.35
        elif mean_interval < 0.5:
            # Mittel
            params['onset_threshold'] = 0.55
            params['frame_threshold'] = 0.45
        else:
            # Langsam: höhere Schwellenwerte für weniger Artefakte
            params['onset_threshold'] = 0.65
            params['frame_threshold'] = 0.55
        
        # === 4. POLYPHONIE → melodia_trick ===
        spectral_flatness = analysis.get('polyphony_spectral_flatness', 0.5)
        
        # Hohe Flatness = eher monophon → melodia_trick aktivieren
        # Niedrige Flatness = eher polyphon → melodia_trick deaktivieren
        params['melodia_trick'] = spectral_flatness > 0.35
        
        return params
    
    def _adjust_for_tempo(
        self, 
        params: Dict[str, Any], 
        tempo: float
    ) -> Dict[str, Any]:
        """Passt minimum_note_length basierend auf Tempo an.
        
        Bei langsamen Stücken (60 BPM) sind die Noten doppelt so lang wie bei 120 BPM,
        daher sollte minimum_note_length entsprechend skaliert werden.
        """
        # Basis-Notenlänge aus Preset
        base_min_note = params.get('minimum_note_length', 127)
        
        # Skaliere proportional zum Tempo
        # Bei 60 BPM: Faktor 2.0 → Notenlänge verdoppeln
        # Bei 180 BPM: Faktor 0.67 → Notenlänge reduzieren
        tempo_factor = BASE_TEMPO / max(tempo, 30)  # Vermeide Division durch sehr kleine Werte
        
        # Skaliere und begrenzen
        new_min_note = base_min_note * tempo_factor
        new_min_note = self._clamp(new_min_note, *PARAM_BOUNDS['minimum_note_length'])
        
        params['minimum_note_length'] = int(new_min_note)
        
        return params
    
    def _adjust_frequency_range(
        self, 
        params: Dict[str, Any], 
        min_pitch: float,
        max_pitch: float
    ) -> Dict[str, Any]:
        """Passt den Frequenzbereich an den erkannten Tonhöhenbereich an.
        
        Der Preset-Bereich wird nur eingeengt, nie erweitert.
        Das verhindert, dass z.B. ein Gesangs-Preset plötzlich Bass-Frequenzen erkennt.
        """
        # Etwas Puffer hinzufügen (20% nach unten, 20% nach oben)
        analyzed_min = min_pitch * 0.8
        analyzed_max = max_pitch * 1.2
        
        # Preset-Grenzen
        preset_min = params.get('minimum_frequency', 27.5)
        preset_max = params.get('maximum_frequency', 4186)
        
        # Nur einengen: Maximum von Preset-Min und Analyse-Min
        new_min = max(preset_min, analyzed_min)
        # Nur einengen: Minimum von Preset-Max und Analyse-Max
        new_max = min(preset_max, analyzed_max)
        
        # Sicherheitsprüfung: min muss kleiner als max sein
        if new_min < new_max:
            params['minimum_frequency'] = self._clamp(new_min, *PARAM_BOUNDS['minimum_frequency'])
            params['maximum_frequency'] = self._clamp(new_max, *PARAM_BOUNDS['maximum_frequency'])
        
        return params
    
    def _adjust_for_polyphony(
        self, 
        params: Dict[str, Any], 
        spectral_flatness: float
    ) -> Dict[str, Any]:
        """Passt melodia_trick basierend auf Polyphonie an.
        
        Niedrige spectral_flatness = mehr harmonische Struktur = eher polyphon
        Hohe spectral_flatness = mehr Rauschen/einfache Struktur = eher monophon
        
        melodia_trick ist gut für monophone Melodien - nur überschreiben wenn
        die Analyse stark vom Preset abweicht.
        """
        preset_melodia = params.get('melodia_trick', False)
        
        # Schwellenwert für "wahrscheinlich monophon"
        is_likely_monophonic = spectral_flatness > 0.4
        
        # Nur überschreiben wenn starke Abweichung
        if is_likely_monophonic and not preset_melodia:
            # Analyse sagt monophon, Preset sagt polyphon → Analyse vertrauen
            params['melodia_trick'] = True
        elif not is_likely_monophonic and preset_melodia and spectral_flatness < 0.2:
            # Sehr polyphones Stück, obwohl Preset monophon erwartet
            params['melodia_trick'] = False
        
        return params
    
    def _adjust_for_density(
        self, 
        params: Dict[str, Any], 
        mean_interval: float
    ) -> Dict[str, Any]:
        """Passt onset_threshold basierend auf Notendichte an.
        
        Schnelle Passagen (kurze Intervalle) brauchen niedrigere Schwellenwerte.
        Langsame Passagen (lange Intervalle) können höhere Schwellenwerte haben.
        """
        old_onset = params.get('onset_threshold', 0.5)
        
        if mean_interval < 0.2:  # Sehr schnell (< 200ms zwischen Noten)
            # Senke threshold für bessere Erkennung schneller Noten
            new_onset = old_onset - 0.1
        elif mean_interval > 0.8:  # Langsam (> 800ms zwischen Noten)
            # Erhöhe threshold für weniger Artefakte
            new_onset = old_onset + 0.1
        else:
            new_onset = old_onset
        
        params['onset_threshold'] = self._clamp(new_onset, *PARAM_BOUNDS['onset_threshold'])
        
        return params
    
    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        """Begrenzt einen Wert auf ein Intervall."""
        return max(min_val, min(max_val, value))

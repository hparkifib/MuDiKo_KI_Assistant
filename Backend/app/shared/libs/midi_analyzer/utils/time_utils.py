"""
Hilfsfunktionen für Zeit- und Takt-Berechnungen
"""

from typing import Tuple, List, Dict, Any
import unicodedata
import os


def normalize_filepath(filepath: str) -> str:
    """
    Normalisiert den Dateipfad für Unicode-Kompatibilität
    
    Args:
        filepath: Pfad zur Datei
    
    Returns:
        Normalisierter Pfad
    """
    # Normalisiere zu NFC (composed form)
    normalized = unicodedata.normalize('NFC', filepath)
    
    # Wenn die Datei nicht existiert, versuche NFD (decomposed form)
    if not os.path.exists(normalized):
        normalized = unicodedata.normalize('NFD', filepath)
    
    return normalized


def calculate_bar_and_beat(
    tick_time: int,
    ticks_per_beat: int,
    time_signatures: List[Dict[str, Any]]
) -> Tuple[int, int, int]:
    """
    Berechnet Takt und Zählzeit aus der Tick-Zeit
    
    Args:
        tick_time: Zeit in Ticks
        ticks_per_beat: Ticks pro Beat
        time_signatures: Liste der Taktart-Änderungen
    
    Returns:
        Tuple von (Takt, Zählzeit, Tick_im_Beat)
    """
    if not time_signatures:
        # Standard: 4/4 Takt
        time_signatures = [{'time': 0, 'numerator': 4, 'denominator': 4}]
    
    current_bar = 1
    current_beat = 1
    current_tick_in_beat = 0
    
    # Sortiere Taktwechsel nach Zeit
    sorted_ts = sorted(time_signatures, key=lambda x: x['time'])
    
    # Finde aktuelle Taktart
    current_ts = sorted_ts[0]
    current_time = 0
    
    for ts in sorted_ts:
        if ts['time'] <= tick_time:
            # Berechne Takte bis zu diesem Taktwechsel
            if current_time < ts['time']:
                ticks_per_bar = ticks_per_beat * current_ts['numerator']
                ticks_passed = ts['time'] - current_time
                bars_passed = ticks_passed // ticks_per_bar
                current_bar += bars_passed
                current_time = ts['time']
            current_ts = ts
        else:
            break
    
    # Berechne Position in aktuellem Takt
    ticks_per_bar = ticks_per_beat * current_ts['numerator']
    ticks_from_last_ts = tick_time - current_time
    
    bars_from_last_ts = ticks_from_last_ts // ticks_per_bar
    current_bar += bars_from_last_ts
    
    ticks_in_current_bar = ticks_from_last_ts % ticks_per_bar
    current_beat = (ticks_in_current_bar // ticks_per_beat) + 1
    current_tick_in_beat = ticks_in_current_bar % ticks_per_beat
    
    return current_bar, current_beat, current_tick_in_beat


def format_time_info(
    tick_time: int,
    ticks_per_beat: int,
    time_signatures: List[Dict[str, Any]],
    length_seconds: float
) -> str:
    """
    Formatiert Zeit-Informationen (Takt, Zählzeit, Zeit)
    
    Args:
        tick_time: Zeit in Ticks
        ticks_per_beat: Ticks pro Beat
        time_signatures: Liste der Taktart-Änderungen
        length_seconds: Länge der Datei in Sekunden
    
    Returns:
        Formatierter String wie "T3.2+120 (Zeit: 1440, ~2.50s)"
    """
    bar, beat, tick_in_beat = calculate_bar_and_beat(tick_time, ticks_per_beat, time_signatures)
    time_seconds = tick_time / ticks_per_beat * 0.5  # Approximation
    
    return f"T{bar}.{beat}+{tick_in_beat:3d} (Zeit: {tick_time:6d}, ~{time_seconds:.2f}s)"


def get_bar_beat_string(bar: int, beat: int) -> str:
    """
    Gibt einen formatierten Takt.Schlag String zurück
    
    Args:
        bar: Taktnummer
        beat: Schlag/Beat-Nummer
    
    Returns:
        String wie "T3.2"
    """
    return f"T{bar}.{beat}"


def get_position_key(bar: int, beat: int) -> str:
    """
    Gibt einen Position-Key für Dictionaries zurück
    
    Args:
        bar: Taktnummer
        beat: Schlag/Beat-Nummer
    
    Returns:
        String wie "Takt 3, Zählzeit 2"
    """
    return f"Takt {bar}, Zählzeit {beat}"

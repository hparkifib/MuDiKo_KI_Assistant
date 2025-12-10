"""
Utility-Funktionen für MIDI-Analyse
"""

from .music_theory import (
    note_number_to_name,
    classify_interval,
    classify_duration,
    classify_dynamic,
    get_dynamic_name,
    get_average_dynamic_name,
    get_instrument_name,
    get_movement_description
)

from .time_utils import (
    normalize_filepath,
    calculate_bar_and_beat,
    format_time_info,
    get_bar_beat_string,
    get_position_key
)

__all__ = [
    # Music Theory
    'note_number_to_name',
    'classify_interval',
    'classify_duration',
    'classify_dynamic',
    'get_dynamic_name',
    'get_average_dynamic_name',
    'get_instrument_name',
    'get_movement_description',
    # Time Utils
    'normalize_filepath',
    'calculate_bar_and_beat',
    'format_time_info',
    'get_bar_beat_string',
    'get_position_key',
]

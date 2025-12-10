"""
Datenmodelle für MIDI-Rohdaten
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Note:
    """Eine einzelne MIDI-Note"""
    time: int
    note_number: int
    note_name: str
    velocity: int
    duration: int = 0
    bar: int = 0
    beat: int = 0
    tick_in_beat: int = 0
    duration_type: str = ""
    dynamic: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'note_number': self.note_number,
            'note_name': self.note_name,
            'velocity': self.velocity,
            'duration': self.duration,
            'bar': self.bar,
            'beat': self.beat,
            'tick_in_beat': self.tick_in_beat,
            'duration_type': self.duration_type,
            'dynamic': self.dynamic
        }


@dataclass
class TempoChange:
    """Tempo-Änderung"""
    time: int
    tempo: int
    bpm: float
    bar: int = 0
    beat: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'tempo': self.tempo,
            'bpm': self.bpm,
            'bar': self.bar,
            'beat': self.beat
        }


@dataclass
class TimeSignature:
    """Taktart"""
    time: int
    numerator: int
    denominator: int
    clocks_per_click: int = 24
    notated_32nd_notes_per_beat: int = 8
    bar: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'numerator': self.numerator,
            'denominator': self.denominator,
            'bar': self.bar,
            'signature': f"{self.numerator}/{self.denominator}"
        }


@dataclass
class KeySignature:
    """Tonart"""
    time: int
    key: str
    bar: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'key': self.key,
            'bar': self.bar
        }


@dataclass
class ProgramChange:
    """Instrumentenwechsel"""
    time: int
    program: int
    instrument: str
    bar: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'program': self.program,
            'instrument': self.instrument,
            'bar': self.bar
        }


@dataclass
class ControlChange:
    """Control Change Event"""
    time: int
    control: int
    value: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'control': self.control,
            'value': self.value
        }


@dataclass
class PedalEvent:
    """Pedal-Event"""
    time: int
    state: str  # "gedrückt" oder "losgelassen"
    value: int
    bar: int = 0
    beat: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'state': self.state,
            'value': self.value,
            'bar': self.bar,
            'beat': self.beat
        }


@dataclass
class TrackData:
    """Ein MIDI-Track mit allen Events"""
    track_number: int
    track_name: str
    notes: List[Note] = field(default_factory=list)
    tempo_changes: List[TempoChange] = field(default_factory=list)
    time_signatures: List[TimeSignature] = field(default_factory=list)
    key_signatures: List[KeySignature] = field(default_factory=list)
    program_changes: List[ProgramChange] = field(default_factory=list)
    control_changes: List[ControlChange] = field(default_factory=list)
    pedal_events: List[PedalEvent] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'track_number': self.track_number,
            'track_name': self.track_name,
            'notes': [n.to_dict() for n in self.notes],
            'tempo_changes': [t.to_dict() for t in self.tempo_changes],
            'time_signatures': [ts.to_dict() for ts in self.time_signatures],
            'key_signatures': [ks.to_dict() for ks in self.key_signatures],
            'program_changes': [pc.to_dict() for pc in self.program_changes],
            'pedal_events': [pe.to_dict() for pe in self.pedal_events]
        }


@dataclass
class MidiData:
    """Komplette MIDI-Datei-Daten"""
    filename: str
    midi_type: int
    ticks_per_beat: int
    length_seconds: float
    tracks: List[TrackData] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'midi_type': self.midi_type,
            'ticks_per_beat': self.ticks_per_beat,
            'length_seconds': self.length_seconds,
            'tracks': [t.to_dict() for t in self.tracks]
        }

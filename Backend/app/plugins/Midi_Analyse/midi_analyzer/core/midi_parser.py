"""
MIDI Parser - Liest MIDI-Dateien und extrahiert Rohdaten
"""

from mido import MidiFile, tempo2bpm
from collections import defaultdict
from typing import List, Union, BinaryIO
import io

from ..models.midi_data import (
    MidiData, TrackData, Note, TempoChange, TimeSignature,
    KeySignature, ProgramChange, ControlChange, PedalEvent
)
from ..utils import (
    note_number_to_name, normalize_filepath, calculate_bar_and_beat,
    classify_duration, classify_dynamic, get_instrument_name
)


class MidiParser:
    """
    Parst MIDI-Dateien und extrahiert alle relevanten Daten
    Thread-safe für Backend-Nutzung
    """
    
    def parse_file(self, filepath: str) -> MidiData:
        """
        Parst eine MIDI-Datei vom Dateisystem
        
        Args:
            filepath: Pfad zur MIDI-Datei
        
        Returns:
            MidiData-Objekt mit allen extrahierten Daten
        
        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn Datei kein gültiges MIDI ist
        """
        filepath = normalize_filepath(filepath)
        midi = MidiFile(filepath)
        return self._parse_midi(midi, filepath)
    
    def parse_bytes(self, data: bytes, filename: str = "uploaded.mid") -> MidiData:
        """
        Parst MIDI-Daten aus Bytes (für File-Uploads)
        
        Args:
            data: MIDI-Datei als Bytes
            filename: Optionaler Dateiname für Referenz
        
        Returns:
            MidiData-Objekt mit allen extrahierten Daten
        
        Raises:
            ValueError: Wenn Daten kein gültiges MIDI sind
        """
        try:
            file_like = io.BytesIO(data)
            midi = MidiFile(file=file_like)
            return self._parse_midi(midi, filename)
        except Exception as e:
            raise ValueError(f"Ungültige MIDI-Daten: {str(e)}")
    
    def _parse_midi(self, midi: MidiFile, filename: str) -> MidiData:
        """
        Interne Methode zum Parsen eines MidiFile-Objekts
        
        Args:
            midi: MidiFile-Objekt von mido
            filename: Dateiname für Referenz
        
        Returns:
            MidiData-Objekt
        """
        midi_data = MidiData(
            filename=filename,
            midi_type=midi.type,
            ticks_per_beat=midi.ticks_per_beat,
            length_seconds=midi.length
        )
        
        # Parse jeden Track
        for track_num, track in enumerate(midi.tracks):
            track_data = self._parse_track(
                track, track_num, midi.ticks_per_beat
            )
            midi_data.tracks.append(track_data)
        
        return midi_data
    
    def _parse_track(
        self, track, track_number: int, ticks_per_beat: int
    ) -> TrackData:
        """
        Parst einen einzelnen MIDI-Track
        
        Args:
            track: MIDI Track von mido
            track_number: Track-Nummer
            ticks_per_beat: Ticks pro Beat
        
        Returns:
            TrackData-Objekt
        """
        track_name = track.name if hasattr(track, 'name') else f"Track {track_number}"
        
        track_data = TrackData(
            track_number=track_number,
            track_name=track_name
        )
        
        absolute_time = 0
        active_notes = defaultdict(lambda: {'start_time': 0, 'velocity': 0})
        time_signatures = []
        
        for msg in track:
            absolute_time += msg.time
            
            # Note Events
            if msg.type == 'note_on' and msg.velocity > 0:
                note = Note(
                    time=absolute_time,
                    note_number=msg.note,
                    note_name=note_number_to_name(msg.note),
                    velocity=msg.velocity,
                    dynamic=classify_dynamic(msg.velocity)
                )
                track_data.notes.append(note)
                active_notes[msg.note] = {
                    'start_time': absolute_time,
                    'velocity': msg.velocity,
                    'note_obj': note
                }
                
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_info = active_notes[msg.note]
                    duration = absolute_time - start_info['start_time']
                    
                    # Update das Note-Objekt mit Duration
                    note_obj = start_info['note_obj']
                    note_obj.duration = duration
                    note_obj.duration_type = classify_duration(duration, ticks_per_beat)
                    
                    del active_notes[msg.note]
            
            # Tempo Changes
            elif msg.type == 'set_tempo':
                tempo = TempoChange(
                    time=absolute_time,
                    tempo=msg.tempo,
                    bpm=round(tempo2bpm(msg.tempo), 2)
                )
                track_data.tempo_changes.append(tempo)
            
            # Time Signature
            elif msg.type == 'time_signature':
                ts = TimeSignature(
                    time=absolute_time,
                    numerator=msg.numerator,
                    denominator=msg.denominator,
                    clocks_per_click=msg.clocks_per_click,
                    notated_32nd_notes_per_beat=msg.notated_32nd_notes_per_beat
                )
                track_data.time_signatures.append(ts)
                time_signatures.append({
                    'time': absolute_time,
                    'numerator': msg.numerator,
                    'denominator': msg.denominator
                })
            
            # Key Signature
            elif msg.type == 'key_signature':
                ks = KeySignature(
                    time=absolute_time,
                    key=msg.key
                )
                track_data.key_signatures.append(ks)
            
            # Program Change (Instrument)
            elif msg.type == 'program_change':
                pc = ProgramChange(
                    time=absolute_time,
                    program=msg.program,
                    instrument=get_instrument_name(msg.program)
                )
                track_data.program_changes.append(pc)
            
            # Control Changes
            elif msg.type == 'control_change':
                cc = ControlChange(
                    time=absolute_time,
                    control=msg.control,
                    value=msg.value
                )
                track_data.control_changes.append(cc)
                
                # Sustain Pedal (Control 64)
                if msg.control == 64:
                    pedal_state = "gedrückt" if msg.value >= 64 else "losgelassen"
                    pedal = PedalEvent(
                        time=absolute_time,
                        state=pedal_state,
                        value=msg.value
                    )
                    track_data.pedal_events.append(pedal)
        
        # Berechne Bar/Beat für alle Noten und Events
        self._calculate_positions(track_data, ticks_per_beat, time_signatures)
        
        return track_data
    
    def _calculate_positions(
        self, track_data: TrackData, ticks_per_beat: int,
        time_signatures: List[dict]
    ):
        """
        Berechnet Takt und Beat-Positionen für alle Events
        
        Args:
            track_data: TrackData-Objekt
            ticks_per_beat: Ticks pro Beat
            time_signatures: Liste der Taktarten
        """
        # Für Noten
        for note in track_data.notes:
            bar, beat, tick = calculate_bar_and_beat(
                note.time, ticks_per_beat, time_signatures
            )
            note.bar = bar
            note.beat = beat
            note.tick_in_beat = tick
        
        # Für Tempo Changes
        for tempo in track_data.tempo_changes:
            bar, beat, _ = calculate_bar_and_beat(
                tempo.time, ticks_per_beat, time_signatures
            )
            tempo.bar = bar
            tempo.beat = beat
        
        # Für Time Signatures
        for ts in track_data.time_signatures:
            bar, _, _ = calculate_bar_and_beat(
                ts.time, ticks_per_beat, time_signatures
            )
            ts.bar = bar
        
        # Für Key Signatures
        for ks in track_data.key_signatures:
            bar, _, _ = calculate_bar_and_beat(
                ks.time, ticks_per_beat, time_signatures
            )
            ks.bar = bar
        
        # Für Program Changes
        for pc in track_data.program_changes:
            bar, _, _ = calculate_bar_and_beat(
                pc.time, ticks_per_beat, time_signatures
            )
            pc.bar = bar
        
        # Für Pedal Events
        for pedal in track_data.pedal_events:
            bar, beat, _ = calculate_bar_and_beat(
                pedal.time, ticks_per_beat, time_signatures
            )
            pedal.bar = bar
            pedal.beat = beat

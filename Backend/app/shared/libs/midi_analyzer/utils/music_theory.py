"""
Hilfsfunktionen für Musiktheorie
"""

from typing import Dict


def note_number_to_name(note_number: int) -> str:
    """
    Konvertiert MIDI-Note-Nummer zu Note-Namen
    
    Args:
        note_number: MIDI-Notennummer (0-127)
    
    Returns:
        Note-Name wie "C4", "A#5", etc.
    """
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_number // 12) - 1
    note_name = notes[note_number % 12]
    return f"{note_name}{octave}"


def classify_interval(semitones: int) -> str:
    """
    Klassifiziert musikalische Intervalle
    
    Args:
        semitones: Anzahl der Halbtöne
    
    Returns:
        Deutscher Name des Intervalls
    """
    interval_map = {
        0: "Prime",
        1: "kleine Sekunde",
        2: "große Sekunde",
        3: "kleine Terz",
        4: "große Terz",
        5: "Quarte",
        6: "Tritonus",
        7: "Quinte",
        8: "kleine Sexte",
        9: "große Sexte",
        10: "kleine Septime",
        11: "große Septime",
        12: "Oktave"
    }
    
    if semitones <= 12:
        return interval_map.get(semitones, f"{semitones} Halbtöne")
    else:
        octaves = semitones // 12
        remainder = semitones % 12
        base = interval_map.get(remainder, f"{remainder} Halbtöne")
        return f"{base} + {octaves} Oktave(n)"


def classify_duration(duration_ticks: int, ticks_per_beat: int) -> str:
    """
    Klassifiziert die Notenlänge
    
    Args:
        duration_ticks: Dauer in Ticks
        ticks_per_beat: Ticks pro Beat
    
    Returns:
        Name der Notenlänge (z.B. "Viertel Note")
    """
    ratio = duration_ticks / ticks_per_beat
    
    if ratio >= 3.75:
        return "Ganze Note"
    elif ratio >= 1.75:
        return "Halbe Note"
    elif ratio >= 0.875:
        return "Viertel Note"
    elif ratio >= 0.4375:
        return "Achtel Note"
    elif ratio >= 0.21875:
        return "Sechzehntel Note"
    elif ratio >= 0.109375:
        return "Zweiunddreißigstel Note"
    else:
        return "Sehr kurz"


def classify_dynamic(velocity: int) -> str:
    """
    Klassifiziert Velocity zu Dynamik-Bezeichnung
    
    Args:
        velocity: MIDI Velocity (0-127)
    
    Returns:
        Dynamik-Bezeichnung (ppp, pp, p, mp, mf, f, ff, fff)
    """
    if velocity <= 16:
        return "ppp"
    elif velocity <= 32:
        return "pp"
    elif velocity <= 48:
        return "p"
    elif velocity <= 64:
        return "mp"
    elif velocity <= 80:
        return "mf"
    elif velocity <= 96:
        return "f"
    elif velocity <= 112:
        return "ff"
    else:
        return "fff"


def get_dynamic_name(dynamic_code: str) -> str:
    """
    Gibt den deutschen Namen einer Dynamik-Bezeichnung zurück
    
    Args:
        dynamic_code: Dynamik-Code (ppp, pp, p, mp, mf, f, ff, fff)
    
    Returns:
        Deutscher Name
    """
    dynamic_names = {
        'ppp': 'sehr, sehr leise',
        'pp': 'sehr leise',
        'p': 'leise',
        'mp': 'mittelleise',
        'mf': 'mittellaut',
        'f': 'laut',
        'ff': 'sehr laut',
        'fff': 'sehr, sehr laut'
    }
    return dynamic_names.get(dynamic_code, dynamic_code)


def get_average_dynamic_name(avg_velocity: float) -> str:
    """
    Gibt deutschen Namen für durchschnittliche Lautstärke
    
    Args:
        avg_velocity: Durchschnittliche Velocity
    
    Returns:
        Beschreibung der Durchschnittslautstärke
    """
    if avg_velocity <= 48:
        return "leise (piano)"
    elif avg_velocity <= 64:
        return "mittelleise (mezzo-piano)"
    elif avg_velocity <= 80:
        return "mittellaut (mezzo-forte)"
    elif avg_velocity <= 96:
        return "laut (forte)"
    else:
        return "sehr laut (fortissimo)"


def get_instrument_name(program_number: int) -> str:
    """
    Gibt den General MIDI Instrumentnamen zurück
    
    Args:
        program_number: MIDI Program Number (0-127)
    
    Returns:
        Name des Instruments
    """
    instruments = [
        # Piano (0-7)
        "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano",
        "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
        # Chromatic Percussion (8-15)
        "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
        # Organ (16-23)
        "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion",
        "Harmonica", "Tango Accordion",
        # Guitar (24-31)
        "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)",
        "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics",
        # Bass (32-39)
        "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
        "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
        # Strings (40-47)
        "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
        # Ensemble (48-55)
        "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2",
        "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
        # Brass (56-63)
        "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
        # Reed (64-71)
        "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet",
        # Pipe (72-79)
        "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
        # Synth Lead (80-87)
        "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)",
        "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
        # Synth Pad (88-95)
        "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
        "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
        # Synth Effects (96-103)
        "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
        "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
        # Ethnic (104-111)
        "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag pipe", "Fiddle", "Shanai",
        # Percussive (112-119)
        "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
        # Sound Effects (120-127)
        "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
    ]
    if 0 <= program_number < len(instruments):
        return instruments[program_number]
    return f"Unknown ({program_number})"


def get_movement_description(max_leap: int) -> str:
    """
    Beschreibt die Melodiebewegung basierend auf dem größten Sprung
    
    Args:
        max_leap: Größter Sprung in Halbtönen
    
    Returns:
        Beschreibung der Melodiebewegung
    """
    if max_leap <= 2:
        return "Die Melodie bewegt sich in sehr kleinen Schritten"
    elif max_leap <= 5:
        return "Die Melodie bewegt sich in kleinen bis mittleren Schritten"
    elif max_leap <= 12:
        return "Die Melodie enthält einige größere Sprünge"
    else:
        return "Die Melodie enthält sehr große Sprünge (über eine Oktave)"

"""
MP3-to-MIDI Conversion Presets

Dieses Package enthält vordefinierte Presets für verschiedene Instrumente.
Jedes Preset ist als JSON-Datei gespeichert und enthält optimierte Parameter
für die Basic Pitch MIDI-Konvertierung.

Verfügbare Presets (englische Dateinamen):
- piano.json: Piano/Keyboard (polyphon)
- vocals.json: Singstimmen (monophon)
- woodwinds.json: Flute, Clarinet, Oboe, Bassoon (monophon)
- brass.json: Trumpet, Trombone, Horn, Tuba (monophon)
- strings.json: Violin, Viola, Cello, Double Bass (meist polyphon)
- guitar.json: Acoustic/Electric Guitar (polyphon)
- ensemble.json: Mixed instruments (polyphon)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class PresetManager:
    """Manager für das Laden und Verwalten von Conversion-Presets"""
    
    def __init__(self):
        self.presets_dir = Path(__file__).parent
        self._presets_cache: Optional[Dict[str, dict]] = None
        self._allowed_ids = {
            "piano", "guitar", "vocals", "woodwinds", "brass", "strings", "ensemble"
        }
        # Legacy-ID-Mapping (Deutsch -> Englisch). 'schlagzeug' wurde entfernt.
        self._legacy_alias = {
            "klavier": "piano",
            "gitarre": "guitar",
            "gesang": "vocals",
            "holzblaeser": "woodwinds",
            "blechblaeser": "brass",
            "streicher": "strings",
            "schlagzeug": None,
        }
    
    def load_preset(self, preset_id: str) -> dict:
        """
        Lädt ein einzelnes Preset anhand seiner ID.
        
        Args:
            preset_id: ID des Presets (z.B. 'klavier', 'gesang')
            
        Returns:
            Dict mit Preset-Daten
            
        Raises:
            FileNotFoundError: Wenn Preset nicht existiert
            json.JSONDecodeError: Wenn JSON ungültig ist
        """
        # Legacy Alias unterstützen
        if preset_id in self._legacy_alias:
            mapped = self._legacy_alias[preset_id]
            if mapped is None:
                raise FileNotFoundError("Das 'drums'/'schlagzeug' Preset wurde entfernt, da Tonhöhen-Transkription dafür ungeeignet ist.")
            preset_id = mapped

        preset_path = self.presets_dir / f"{preset_id}.json"
        
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset '{preset_id}' nicht gefunden: {preset_path}")
        
        with open(preset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_presets(self) -> Dict[str, dict]:
        """
        Lädt alle verfügbaren Presets.
        
        Returns:
            Dict mit preset_id -> preset_data Mapping
        """
        if self._presets_cache is not None:
            return self._presets_cache
        
        presets = {}
        for preset_file in self.presets_dir.glob("*.json"):
            preset_id = preset_file.stem
            # Nur neue englische Presets laden
            if preset_id not in self._allowed_ids:
                continue
            try:
                presets[preset_id] = self.load_preset(preset_id)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warnung: Konnte Preset '{preset_id}' nicht laden: {e}")
        
        self._presets_cache = presets
        return presets
    
    def get_preset_list(self) -> List[dict]:
        """
        Gibt eine Liste aller Presets mit Basis-Informationen zurück.
        Nützlich für Frontend-Dropdowns.
        
        Returns:
            Liste von Dicts mit id, name, icon, description, instruments
        """
        all_presets = self.load_all_presets()
        return [
            {
                'id': preset.get('id') or preset.get('file_id', ''),
                'name': preset['name'],
                'icon': preset.get('icon', ''),
                'description': preset.get('description', ''),
                'instruments': preset.get('instruments', [])
            }
            for preset in all_presets.values()
        ]
    
    def get_preset_parameters(self, preset_id: str) -> dict:
        """
        Gibt nur die Basic Pitch Parameter eines Presets zurück.
        
        Args:
            preset_id: ID des Presets
            
        Returns:
            Dict mit Basic Pitch Parametern
        """
        preset = self.load_preset(preset_id)
        return preset.get('parameters', {})
    
    def get_preprocessing_config(self, preset_id: str) -> dict:
        """
        Gibt die Preprocessing-Konfiguration eines Presets zurück.
        
        Args:
            preset_id: ID des Presets
            
        Returns:
            Dict mit Preprocessing-Flags
        """
        preset = self.load_preset(preset_id)
        return preset.get('preprocessing', {})


# Singleton-Instanz für einfachen Import
preset_manager = PresetManager()


def get_preset(preset_id: str) -> dict:
    """Convenience-Funktion zum Laden eines Presets"""
    return preset_manager.load_preset(preset_id)


def list_presets() -> List[dict]:
    """Convenience-Funktion zum Auflisten aller Presets"""
    return preset_manager.get_preset_list()

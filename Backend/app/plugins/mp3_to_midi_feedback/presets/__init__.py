"""
MP3-to-MIDI Conversion Presets

Dieses Package enthält vordefinierte Presets für verschiedene Instrumente.
Jedes Preset ist als JSON-Datei gespeichert und enthält optimierte Parameter
für die Basic Pitch MIDI-Konvertierung.

Verfügbare Presets:
- klavier.json: Klavier/Keyboard (polyphon)
- gesang.json: Singstimmen (monophon)
- holzblaeser.json: Flöte, Klarinette, Oboe
- blechblaeser.json: Trompete, Posaune, Horn
- streicher.json: Violine, Cello, Kontrabass
- gitarre.json: Akustik-/E-Gitarre
- schlagzeug.json: Drums, Percussion
- ensemble.json: Gemischte Instrumente
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class PresetManager:
    """Manager für das Laden und Verwalten von Conversion-Presets"""
    
    def __init__(self):
        self.presets_dir = Path(__file__).parent
        self._presets_cache: Optional[Dict[str, dict]] = None
    
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
            Liste von Dicts mit id, name, icon, description
        """
        all_presets = self.load_all_presets()
        return [
            {
                'id': preset['id'],
                'name': preset['name'],
                'icon': preset['icon'],
                'description': preset['description'],
                'use_case': preset.get('use_case', ''),
                'target_group': preset.get('target_group', '')
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

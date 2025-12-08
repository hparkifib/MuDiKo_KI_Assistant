# AudioManager - Klasse für die Verwaltung von Audio-Dateien
# Behandelt Upload, Speicherung, Segmentierung und Serving von Audio-Dateien

import os
from typing import Optional
from flask import Blueprint, send_from_directory
import librosa  # Audio-Verarbeitung und -Analyse
import soundfile as sf  # Audio-Datei Ein-/Ausgabe
import uuid  # Eindeutige Dateinamen für Segmente
import numpy as np  # Numerische Operationen für Audio-Daten

class AudioManager:
    """Verwaltet Audio-Dateien für die mudiko-Anwendung.
    
    Diese Klasse behandelt:
    - Upload und Speicherung von Audio-Dateien
    - Segmentierung von Audio-Dateien in kleinere Abschnitte
    - Serving von Dateien über Flask-Blueprint
    - Verwaltung von Original-Dateinamen
    """
    
    def __init__(self, upload_folder: str):
        """Initialisiert den AudioManager.
        
        Args:
            upload_folder: Pfad zum Ordner für hochgeladene Dateien
        """
        self.upload_folder = upload_folder
        # Segments-Ordner wird jetzt pro Session erstellt, nicht global
        # os.makedirs wird bei Bedarf in segment_and_save() aufgerufen

        # Flask-Blueprint für Datei-Serving konfigurieren
        self.bp = Blueprint('audio', __name__)
        self.bp.add_url_rule(
            '/uploads/<filename>',
            endpoint='serve',
            view_func=self.serve
        )

        # Dictionary zur Speicherung der ursprünglichen Dateinamen
        self.original_filenames = {}

    def save_with_role(self, file, role, base_folder: Optional[str] = None):
        """Speichert eine hochgeladene Datei mit einer standardisierten Rolle.
        
        Args:
            file: Flask FileStorage-Objekt der hochgeladenen Datei
            role: Rolle der Datei ('referenz' oder 'schueler')
            
        Returns:
            str: Standardisierter Dateiname (z.B. 'referenz.mp3')
        """
        folder = base_folder if base_folder else self.upload_folder
        # Erstelle standardisierten Dateinamen basierend auf der Rolle
        filename = f"{role}.mp3"
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        
        # Speichere den ursprünglichen Dateinamen für spätere Anzeige
        # Hinweis: original_filenames ist global im Manager; für Multi-Session sollte
        # diese Information außerhalb des Managers pro Session verwaltet werden.
        self.original_filenames[role] = file.filename
        print(f"Datei gespeichert: {filename} (Originalname: {file.filename})")
        return filename

    def get_original_filename(self, role):
        """Gibt den ursprünglichen Dateinamen für eine Rolle zurück."""
        return self.original_filenames.get(role, "Keine Datei hochgeladen")

    def list_files(self, base_folder: Optional[str] = None):
        """Listet nur die hochgeladenen Hauptdateien auf (keine Segmente).
        
        Returns:
            list: Liste der Dateinamen ohne Segment-Dateien
        """
        folder = base_folder if base_folder else self.upload_folder
        if not os.path.exists(folder):
            return []
        return [f for f in os.listdir(folder) if not f.startswith("segment_")]

    def map_files_to_roles(self, files):
        """Erstellt ein Mapping von Rollen zu Dateinamen.
        
        Args:
            files: Liste der verfügbaren Dateien
            
        Returns:
            dict: Mapping von Rollen ('referenz', 'schueler') zu Dateinamen
        """
        return {
            "referenz": "referenz.mp3" if "referenz.mp3" in files else None,
            "schueler": "schueler.mp3" if "schueler.mp3" in files else None
        }

    def delete_all_files(self, base_folder: Optional[str] = None):
        """Löscht alle Hauptdateien im Upload-Ordner.
        
        Segmente werden separat verwaltet und hier nicht gelöscht.
        Fehler beim Löschen werden stillschweigend ignoriert.
        """
        folder = base_folder if base_folder else self.upload_folder
        for f in self.list_files(folder):
            try:
                os.remove(os.path.join(folder, f))
            except Exception:
                # Ignoriere Fehler beim Löschen (z.B. Datei bereits gelöscht)
                pass



    def serve(self, filename: str):
        """Serviert eine Datei über HTTP für Browser-Wiedergabe.
        
        Args:
            filename: Name der zu servierenden Datei
            
        Returns:
            Flask Response-Objekt mit der Datei
        """
        return send_from_directory(self.upload_folder, filename)

    def cleanup_segments(self, original_filenames):
        """Löscht Segment-Dateien für bestimmte Original-Dateien.
        
        Args:
            original_filenames: Liste der Ursprungsdateien deren Segmente gelöscht werden sollen
                               (z.B. ["referenz.wav", "schueler.wav"])
        
        Note:
            Diese Funktion wird aktuell nicht verwendet, da Segmente automatisch
            bei jedem neuen Upload überschrieben werden.
        """
        for orig in original_filenames:
            base = os.path.splitext(orig)[0]  # Dateiname ohne Erweiterung
            for f in self.list_files():
                if f.startswith(base) and "_segment" in f:
                    try:
                        os.remove(os.path.join(self.upload_folder, f))
                    except Exception:
                        # Ignoriere Fehler beim Löschen
                        pass


    def segment_and_save(self, filename, segment_length_sec=8, base_folder: Optional[str] = None):
        """Segmentiert eine Audio-Datei in gleichmäßige Zeitabschnitte.
        
        Diese Funktion teilt eine Audio-Datei in Segmente fester Länge auf,
        um eine detaillierte Analyse zu ermöglichen. Kurze Dateien werden
        mit Stille aufgefüllt, um einheitliche Segmentlängen zu gewährleisten.
        
        Args:
            filename: Name der zu segmentierenden Audio-Datei
            segment_length_sec: Länge jedes Segments in Sekunden (Standard: 8)
            
        Returns:
            list: Liste von Dictionaries mit Segment-Informationen:
                  - filename: Name der Segment-Datei
                  - start_sec: Startzeit des Segments in Sekunden
                  - end_sec: Endzeit des Segments in Sekunden
        """
        # Lade die Audio-Datei
        folder = base_folder if base_folder else self.upload_folder
        os.makedirs(folder, exist_ok=True)
        
        # Erstelle segments-Unterordner innerhalb des Session-Ordners
        segments_folder = os.path.join(folder, "segments")
        os.makedirs(segments_folder, exist_ok=True)
        
        path = os.path.join(folder, filename)
        y, sr = librosa.load(path)  # y = Audio-Daten, sr = Sample Rate
        total_len = len(y)
        segment_samples = int(segment_length_sec * sr)  # Segment-Länge in Samples

        # Berechne Anzahl der benötigten Segmente (aufrunden)
        n_segments = (total_len + segment_samples - 1) // segment_samples
        padded_len = n_segments * segment_samples
        
        # Füge Stille hinzu, falls die Datei zu kurz ist
        if total_len < padded_len:
            y = np.pad(y, (0, padded_len - total_len), mode='constant')

        segments = []
        # Erstelle jedes Segment
        for i in range(n_segments):
            start = i * segment_samples
            end = start + segment_samples
            y_seg = y[start:end]  # Extrahiere Segment-Audio
            
            # Berechne Zeitstempel
            seg_start_sec = start / sr
            seg_end_sec = end / sr
            
            # Erstelle eindeutigen Segment-Dateinamen
            seg_filename = f"{os.path.splitext(filename)[0]}_segment{i+1}_{uuid.uuid4().hex[:8]}.wav"
            seg_path = os.path.join(segments_folder, seg_filename)
            
            # Speichere Segment als WAV-Datei
            sf.write(seg_path, y_seg, sr)
            
            # Füge Segment-Info zur Liste hinzu mit relativem Pfad
            segments.append({
                "filename": os.path.join("segments", seg_filename),  # segments/filename.wav
                "start_sec": seg_start_sec,
                "end_sec": seg_end_sec
            })
        return segments

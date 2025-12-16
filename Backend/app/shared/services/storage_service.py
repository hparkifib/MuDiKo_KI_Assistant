"""Storage Service - Verwaltet Dateispeicherung und Session-Ordner."""

from pathlib import Path
from typing import List, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.core.exceptions import InvalidFileFormatException

class StorageService:
    """Verwaltet Dateispeicherung und -zugriff."""
    
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'midi', 'mid'}
    
    def __init__(self, base_path: str):
        """Initialisiert den Storage Service.
        
        Args:
            base_path: Basis-Pfad für Datei-Speicherung
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file: FileStorage, session_id: str, 
                  filename: Optional[str] = None, 
                  role: Optional[str] = None) -> Path:
        """Speichert eine hochgeladene Datei.
        
        Args:
            file: Flask FileStorage-Objekt
            session_id: Session-ID für Speicherort
            filename: Optionaler Zieldateiname
            role: Optionale Rolle (z.B. 'referenz', 'schueler')
            
        Returns:
            Path: Pfad zur gespeicherten Datei
            
        Raises:
            InvalidFileFormatException: Bei ungültigem Dateiformat
        """
        # Validiere Dateiformat
        if not self._is_allowed_file(file.filename):
            raise InvalidFileFormatException(
                f"Dateiformat nicht erlaubt: {file.filename}"
            )
        
        # Bestimme Zieldateinamen
        if role:
            # Bei Rolle: standardisierter Name (z.B. 'referenz.mp3')
            ext = self._get_extension(file.filename)
            target_filename = f"{role}.{ext}"
        elif filename:
            target_filename = secure_filename(filename)
        else:
            target_filename = secure_filename(file.filename)
        
        # Erstelle Session-Ordner
        session_dir = self.base_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Speichere Datei
        file_path = session_dir / target_filename
        file.save(str(file_path))
        
        print(f"💾 Datei gespeichert: {target_filename} (Session: {session_id})")
        return file_path
    
    def get_file_path(self, session_id: str, filename: str) -> Optional[Path]:
        """Gibt den Pfad zu einer Datei zurück.
        
        Args:
            session_id: Session-ID
            filename: Dateiname
            
        Returns:
            Optional[Path]: Pfad zur Datei oder None wenn nicht vorhanden
        """
        file_path = self.base_path / session_id / filename
        return file_path if file_path.exists() else None
    
    def list_files(self, session_id: str, pattern: str = "*") -> List[str]:
        """Listet alle Dateien in einer Session.
        
        Args:
            session_id: Session-ID
            pattern: Glob-Pattern für Filterung (z.B. "*.mp3")
            
        Returns:
            List[str]: Liste der Dateinamen
        """
        session_dir = self.base_path / session_id
        if not session_dir.exists():
            return []
        
        return [f.name for f in session_dir.glob(pattern) if f.is_file()]
    
    def delete_file(self, session_id: str, filename: str) -> bool:
        """Löscht eine einzelne Datei.
        
        Args:
            session_id: Session-ID
            filename: Zu löschende Datei
            
        Returns:
            bool: True wenn erfolgreich gelöscht
        """
        file_path = self.base_path / session_id / filename
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Datei gelöscht: {filename} (Session: {session_id})")
            return True
        return False
    
    def delete_all_files(self, session_id: str, exclude_pattern: Optional[str] = None):
        """Löscht alle Dateien einer Session (mit optionaler Ausnahme).
        
        Args:
            session_id: Session-ID
            exclude_pattern: Optional - Pattern für Dateien die behalten werden sollen
        """
        session_dir = self.base_path / session_id
        if not session_dir.exists():
            return
        
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                # Überspringen wenn exclude_pattern matched
                if exclude_pattern and file_path.match(exclude_pattern):
                    continue
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"⚠️ Fehler beim Löschen von {file_path.name}: {e}")
    
    def get_session_directory(self, session_id: str) -> Path:
        """Gibt den Pfad zum Session-Verzeichnis zurück.
        
        Args:
            session_id: Session-ID
            
        Returns:
            Path: Pfad zum Session-Verzeichnis
        """
        return self.base_path / session_id
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Prüft ob Dateiformat erlaubt ist.
        
        Args:
            filename: Dateiname
            
        Returns:
            bool: True wenn Format erlaubt
        """
        return '.' in filename and \
               self._get_extension(filename) in self.ALLOWED_EXTENSIONS
    
    def _get_extension(self, filename: str) -> str:
        """Extrahiert die Dateierweiterung.
        
        Args:
            filename: Dateiname
            
        Returns:
            str: Dateierweiterung (lowercase)
        """
        return filename.rsplit('.', 1)[1].lower()

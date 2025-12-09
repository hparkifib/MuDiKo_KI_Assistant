# Session Service - Verwaltet User-Sessions

from typing import Optional, Dict
from pathlib import Path
import threading
import time
import uuid

from app.shared.models.session import Session
from app.core.exceptions import SessionNotFoundException, SessionExpiredException

class SessionService:
    """Verwaltet User-Sessions thread-safe."""
    
    def __init__(self, base_path: str, ttl_seconds: int = 3600, gc_interval: int = 900):
        """Initialisiert den Session Service.
        
        Args:
            base_path: Basis-Pfad für Session-Dateien
            ttl_seconds: Time-to-Live für Sessions in Sekunden (Standard: 1h)
            gc_interval: Garbage Collection Intervall in Sekunden (Standard: 15min)
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.gc_interval = gc_interval
        
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        
        # Starte Garbage Collector
        self._start_gc()
    
    def create_session(self) -> Session:
        """Erstellt eine neue Session.
        
        Returns:
            Session: Neu erstellte Session-Instanz
        """
        session_id = uuid.uuid4().hex
        session = Session(session_id, self.base_path, self.ttl_seconds)
        
        with self._lock:
            self._sessions[session_id] = session
        
        print(f"✅ Session erstellt: {session_id}")
        return session
    
    def get_session(self, session_id: str, touch: bool = True) -> Session:
        """Holt eine Session und validiert sie.
        
        Args:
            session_id: Die Session-ID
            touch: Ob last_access aktualisiert werden soll (Standard: True)
            
        Returns:
            Session: Die gefundene Session
            
        Raises:
            SessionNotFoundException: Wenn Session nicht existiert
            SessionExpiredException: Wenn Session abgelaufen ist
        """
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} nicht gefunden")
        
        if session.is_expired():
            self.end_session(session_id)
            raise SessionExpiredException(f"Session {session_id} ist abgelaufen")
        
        if touch:
            session.touch()
        
        return session
    
    def end_session(self, session_id: str) -> bool:
        """Beendet eine Session und räumt auf.
        
        Args:
            session_id: Die zu beendende Session-ID
            
        Returns:
            bool: True wenn erfolgreich, False wenn Session nicht existierte
        """
        with self._lock:
            session = self._sessions.pop(session_id, None)
        
        if session:
            session.cleanup()
            print(f"🗑️ Session beendet: {session_id}")
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Entfernt alle abgelaufenen Sessions.
        
        Returns:
            int: Anzahl der entfernten Sessions
        """
        with self._lock:
            expired_ids = [
                sid for sid, sess in self._sessions.items() 
                if sess.is_expired()
            ]
        
        for sid in expired_ids:
            self.end_session(sid)
        
        return len(expired_ids)
    
    def get_session_count(self) -> int:
        """Gibt die Anzahl aktiver Sessions zurück.
        
        Returns:
            int: Anzahl aktiver Sessions
        """
        with self._lock:
            return len(self._sessions)
    
    def _start_gc(self):
        """Startet den Garbage Collector Thread."""
        def gc_loop():
            while True:
                time.sleep(self.gc_interval)
                try:
                    cleaned = self.cleanup_expired()
                    if cleaned > 0:
                        print(f"🗑️ Garbage Collection: {cleaned} abgelaufene Session(s) entfernt")
                except Exception as e:
                    print(f"❌ GC Fehler: {e}")
        
        gc_thread = threading.Thread(target=gc_loop, daemon=True, name="SessionGC")
        gc_thread.start()
        print(f"🚀 Session Garbage Collector gestartet (Intervall: {self.gc_interval}s)")

# Konfiguration für MuDiKo KI Assistant

import os
from pathlib import Path
import yaml

class Config:
    """Basis-Konfiguration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '104857600'))  # 100 MB
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / "Uploads"
    PLUGINS_DIR = BASE_DIR / "plugins"
    
    # Session
    SESSION_TTL_SECONDS = int(os.getenv('SESSION_TTL_SECONDS', '7200'))  # 2 Stunden
    SESSION_GC_INTERVAL = int(os.getenv('GC_INTERVAL_SECONDS', '900'))  # 15 Minuten
    
    # Audio Processing
    AUDIO_TARGET_SR = 22050
    AUDIO_TARGET_LENGTH = 60
    AUDIO_SEGMENT_LENGTH = 8
    
    @classmethod
    def load_plugin_config(cls, plugin_name: str) -> dict:
        """Lädt die Konfiguration für ein Plugin."""
        config_file = cls.PLUGINS_DIR / plugin_name / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}

class DevelopmentConfig(Config):
    """Entwicklungs-Konfiguration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Produktions-Konfiguration."""
    DEBUG = False
    TESTING = False
    
    # In Produktion: Strengere Einstellungen
    SESSION_TTL_SECONDS = 1800  # 30 Minuten

class TestingConfig(Config):
    """Test-Konfiguration."""
    TESTING = True
    DEBUG = True

def get_config():
    """Gibt die Config basierend auf Environment zurück."""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

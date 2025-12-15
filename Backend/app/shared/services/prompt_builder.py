"""Shared Prompt Builder - Zentrale Template-Verwaltung für alle Tools."""

from pathlib import Path
from typing import Dict, Optional


class PromptTemplateLoader:
    """Lädt und verwaltet Prompt-Templates für Tools."""
    
    def __init__(self, template_dir: Path):
        """Initialisiert den Template Loader.
        
        Args:
            template_dir: Pfad zum templates/ Verzeichnis des Plugins
        """
        self.template_dir = Path(template_dir)
        self.shared_template_dir = Path(__file__).parent / "templates"
        self.templates: Dict[str, str] = {}
        
    def load_template(self, template_name: str, fallback: str = "") -> str:
        """Lädt ein Template aus Datei.
        
        Sucht zuerst im Plugin-Template-Verzeichnis, dann im shared-Verzeichnis.
        
        Args:
            template_name: Name der Template-Datei (z.B. "system_prompt.txt")
            fallback: Fallback-Text wenn Datei nicht gefunden wird
            
        Returns:
            Template-Inhalt als String
        """
        # Versuche Plugin-spezifisches Template
        plugin_template = self.template_dir / template_name
        if plugin_template.exists():
            try:
                return plugin_template.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {template_name}: {e}")
        
        # Versuche shared Template
        shared_template = self.shared_template_dir / template_name
        if shared_template.exists():
            try:
                return shared_template.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von shared {template_name}: {e}")
        
        # Fallback
        if fallback:
            print(f"ℹ️ Verwende Fallback für {template_name}")
            return fallback
        
        raise FileNotFoundError(f"Template {template_name} nicht gefunden")
    
    def format_template(self, template: str, **kwargs) -> str:
        """Füllt Template mit Variablen.
        
        Args:
            template: Template-String mit {placeholders}
            **kwargs: Variablen zum Füllen
            
        Returns:
            Formatierter String
        """
        return template.format(**kwargs)


class BasePromptBuilder:
    """Basis-Klasse für Prompt-Generierung mit gemeinsamen Features."""
    
    def __init__(self, template_dir: Path):
        """Initialisiert den Prompt Builder.
        
        Args:
            template_dir: Pfad zum Plugin-Template-Verzeichnis
        """
        self.loader = PromptTemplateLoader(template_dir)
        self._load_common_templates()
    
    def _load_common_templates(self):
        """Lädt gemeinsame Templates (simple_language_note)."""
        try:
            self.simple_language_template = self.loader.load_template(
                "simple_language_note.txt",
                fallback="\nWichtiger Hinweis: Verwende besonders einfache, klare und kurze Sätze, "
                        "damit das Feedback für Schüler mit Sprachbarrieren oder Lernschwierigkeiten "
                        "leicht verständlich ist.\n"
            )
        except Exception as e:
            print(f"⚠️ Fehler beim Laden gemeinsamer Templates: {e}")
            self.simple_language_template = ""
    
    def build_simple_language_section(self, use_simple_language: bool) -> str:
        """Erstellt Simple-Language-Sektion.
        
        Args:
            use_simple_language: Ob einfache Sprache verwendet werden soll
            
        Returns:
            Simple-Language-Hinweis oder leerer String
        """
        return self.simple_language_template if use_simple_language else ""
    
    def build_personalization_section(self, personalization: str) -> str:
        """Erstellt Personalisierungs-Sektion.
        
        Args:
            personalization: Personalisierungstext
            prefix: Prefix für die Sektion
            
        Returns:
            Formatierte Personalisierung oder leerer String
        """

        return personalization if personalization else ""

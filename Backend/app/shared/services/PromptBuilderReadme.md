# Shared Prompt Builder - Dokumentation

Zentrale Template-Verwaltung für konsistente Prompt-Generierung über alle Tools hinweg.

## Architektur

```
shared/
└── services/
    ├── prompt_builder.py        # BasePromptBuilder Klasse
    └── templates/
        └── simple_language_note.txt  # Shared Template
```

## Komponenten

### `PromptTemplateLoader`
Lädt Templates mit Fallback-Logik:
1. Sucht im Plugin-Template-Verzeichnis
2. Falls nicht gefunden: Sucht im shared-Template-Verzeichnis
3. Falls nicht gefunden: Verwendet Fallback-String

### `BasePromptBuilder`
Basis-Klasse für alle Prompt-Builder mit gemeinsamen Features:

**Methoden:**
- `build_simple_language_section(use_simple_language: bool)` - Erstellt Simple-Language-Hinweis
- `build_personalization_section(personalization: str, prefix: str)` - Formatiert Personalisierung

## Verwendung in Plugins

### Audio Feedback Plugin
```python
from app.shared.services.prompt_builder import BasePromptBuilder

class PromptGenerator(BasePromptBuilder):
    def __init__(self, ...):
        template_dir = Path(__file__).parent.parent / "templates"
        super().__init__(template_dir)
        # Plugin-spezifische Initialisierung...
```

### MIDI Comparison Plugin
```python
from app.shared.services.prompt_builder import BasePromptBuilder

class MidiComparisonService(BasePromptBuilder):
    def __init__(self, ...):
        template_dir = Path(__file__).parent / "templates"
        super().__init__(template_dir)
        # Plugin-spezifische Initialisierung...
```

## Template-Hierarchie

```
Suche-Reihenfolge für Templates:
1. Plugin-spezifisch:     plugins/{plugin_name}/templates/
2. Shared:                shared/services/templates/
3. Fallback:              Hardcoded in Code
```

## Gemeinsame Features

### Simple Language Support
Beide Tools unterstützen "Einfache Sprache" Option:

**Template:** `simple_language_note.txt`
**Verwendung:**
```python
simple_note = self.build_simple_language_section(use_simple_language=True)
```

**Platzhalter in Prompts:** `{simple_language_note}`

### Personalisierung
Formatiert persönliche Nachrichten konsistent:

```python
personalization = self.build_personalization_section(
    "Bitte auf Rhythmus fokussieren",
    prefix="PERSONALISIERUNG"
)
```

## Vorteile

✅ **DRY**: Gemeinsame Logik an einem Ort
✅ **Konsistenz**: Einheitliche Features über alle Tools
✅ **Wartbarkeit**: Änderungen an shared Features nur einmal nötig
✅ **Flexibilität**: Plugin-spezifische Anpassungen möglich
✅ **Fallback-Sicherheit**: Kein Breaking bei fehlenden Templates

## Neue Tools hinzufügen

1. Erbe von `BasePromptBuilder`:
```python
class MyToolService(BasePromptBuilder):
    def __init__(self, ...):
        template_dir = Path(__file__).parent / "templates"
        super().__init__(template_dir)
```

2. Nutze gemeinsame Features:
```python
simple_note = self.build_simple_language_section(use_simple_language)
personalization = self.build_personalization_section(text)
```

3. Erstelle Plugin-Templates (optional):
- `templates/system_prompt.txt`
- Oder nutze shared Templates automatisch

## Beispiel: Vollständiger Prompt-Build

```python
# Gemeinsame Sektionen
simple_note = self.build_simple_language_section(use_simple_language)
personalization = self.build_personalization_section(user_message)

# Template laden und füllen
prompt = self.loader.format_template(
    self.system_prompt_template,
    language="Deutsch",
    simple_language_note=simple_note,
    personalization_section=personalization
)
```

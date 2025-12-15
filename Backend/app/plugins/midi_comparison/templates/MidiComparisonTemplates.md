# MIDI Comparison Prompt Templates

Dieses Verzeichnis enthält die konfigurierbaren Prompt-Templates für das MIDI Comparison Tool.

## Dateien

### `system_prompt.txt`
Haupt-System-Prompt der dem LLM die Aufgabe erklärt.

**Verfügbare Platzhalter:**
- `{language}` - Feedback-Sprache (z.B. "Deutsch", "English", "Türkçe")
- `{simple_language_note}` - Hinweis für einfache Sprache (automatisch eingefügt bei Aktivierung)
- `{personalization_section}` - Personalisierungstext der Lehrkraft (optional)

## Bearbeitung

1. **Direkt bearbeiten**: Template kann direkt in diesem Ordner bearbeitet werden
2. **Hot-Reload**: Nach Änderungen Backend neu starten (Template wird bei Initialisierung geladen)
3. **Fallback**: Bei Fehler beim Laden wird eingebetteter Standard-Template verwendet

## Beispiel

```python
# Template wird automatisch geladen:
service = MidiComparisonService()

# Template-Variablen werden gefüllt:
system_prompt = service.generate_feedback_prompt(
    language="Deutsch",
    personalization="Fokus auf Rhythmus"
)
```

## Struktur-Empfehlung

Ein guter MIDI-Feedback-Prompt sollte enthalten:
- **Rollenklarheit**: "Du bist ein Musiklehrer..."
- **Aufgabenbeschreibung**: Was soll analysiert werden?
- **Kontext**: MIDI-Vergleichsdaten werden separat bereitgestellt
- **Feedback-Kategorien**: Noten, Rhythmus, Dynamik, etc.
- **Tonalität**: Freundlich, ermutigend, konstruktiv

## Tipps

- **Präzision**: Klare Anweisungen für bessere LLM-Ergebnisse
- **Pädagogik**: Feedback sollte motivierend und lernfördernd sein
- **Flexibilität**: Platzhalter ermöglichen Anpassung pro Nutzer
- **Testen**: Nach Änderungen mit verschiedenen MIDI-Dateien testen

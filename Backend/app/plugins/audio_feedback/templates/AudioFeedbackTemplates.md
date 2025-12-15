# Audio Feedback Prompt Templates

Dieses Verzeichnis enthält die konfigurierbaren Prompt-Templates für das Audio Feedback Tool.

## Dateien

### `system_prompt.txt`
Haupt-System-Prompt der dem LLM die Aufgabe erklärt.

**Verfügbare Platzhalter:**
- `{referenz_instrument}` - Instrument der Lehrkraft (z.B. "Klavier")
- `{schueler_instrument}` - Instrument des Schülers (z.B. "Klavier")
- `{language}` - Feedback-Sprache (z.B. "Deutsch", "English")
- `{simple_language_note}` - Hinweis für einfache Sprache (wird automatisch eingefügt)
- `{personalization_section}` - Persönliche Nachricht der Lehrkraft (optional)

### `simple_language_note.txt`
Hinweistext der bei aktivierter "Einfache Sprache" Option eingefügt wird.

**Verwendung:**
Wird automatisch in `{simple_language_note}` eingefügt wenn der User die Option aktiviert.

## Bearbeitung

1. **Direkt bearbeiten**: Templates können direkt in diesem Ordner bearbeitet werden
2. **Hot-Reload**: Nach Änderungen Backend neu starten (Templates werden bei Initialisierung geladen)
3. **Fallback**: Bei Fehler beim Laden werden eingebettete Standard-Templates verwendet

## Beispiel

```python
# Template wird automatisch geladen:
prompt_generator = PromptGenerator()

# Template-Variablen werden gefüllt:
system_prompt = prompt_generator.generate_feedback_prompt(
    language="Deutsch",
    referenz_instrument="Klavier",
    # ...
)
```

## Tipps

- **Klarheit**: Halte Anweisungen präzise und verständlich
- **Struktur**: Nutze Absätze und Aufzählungen für bessere Lesbarkeit
- **Platzhalter**: Nutze `{variable}` für dynamische Inhalte
- **Testen**: Nach Änderungen mit echten Daten testen

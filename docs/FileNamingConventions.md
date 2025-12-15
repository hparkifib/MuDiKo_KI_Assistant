# File Naming Conventions

## Grundprinzip

**Jeder Dateiname sollte seinen Kontext selbst erklären - ohne Ordnerstruktur anzuschauen!**

## Naming Patterns nach Sprache

### Python (Backend)
- **Dateien**: `snake_case.py`
- **Klassen**: `PascalCase`
- **Funktionen**: `snake_case()`
- **Variablen**: `snake_case`

### JavaScript/React (Frontend)
- **Components**: `PascalCase.jsx`
- **Hooks**: `camelCase.js` (z.B. `useToolStorage.js`)
- **Utils**: `camelCase.js`
- **Ordner**: `kebab-case/`

### Markdown
- **Dokumentation**: `PascalCase.md` (z.B. `FileNamingConventions.md`)
- **README**: `Readme.md` oder spezifisch: `{Context}Readme.md`

## Übersicht

Alle Dateien folgen einer klaren Namenskonvention, die den Kontext sofort erkennbar macht.

## Backend

### Plugin-Dateien
Format: `{plugin_name}_{type}.py`

```
plugins/
├── audio_feedback/
│   ├── audio_feedback_plugin.py    # Plugin-Klasse
│   ├── audio_feedback_service.py   # Business Logic
│   ├── audio_feedback_routes.py    # API-Endpunkte
│   └── audio_feedback_pipeline.py  # Analyse-Pipeline
└── midi_comparison/
    ├── midi_comparison_plugin.py   # Plugin-Klasse
    ├── midi_comparison_service.py  # Business Logic
    └── midi_comparison_routes.py   # API-Endpunkte
```

### Template-Dokumentation
Format: `{ToolName}Templates.md` (PascalCase)

```
plugins/
├── audio_feedback/templates/
│   └── AudioFeedbackTemplates.md
└── midi_comparison/templates/
    └── MidiComparisonTemplates.md
```

### Shared Services
Format: `{service_name}_service.py`

```
shared/services/
├── session_service.py
├── storage_service.py
├── audio_service.py
└── prompt_builder.py
```

## Frontend

### Page Components
Format: `{ToolName}{PageType}Page.jsx`

```
pages/
├── audio-feedback/
│   ├── AudioFeedbackUploadPage.jsx
│   ├── AudioFeedbackRecordingsPage.jsx
│   └── AudioFeedbackInstrumentsPage.jsx
├── midi-comparison/
│   ├── MidiComparisonUploadPage.jsx
│   ├── MidiComparisonLanguagePage.jsx
│   └── MidiComparisonPersonalizationPage.jsx
└── common/
    ├── ToolSelectionPage.jsx
    ├── CommonLanguagePage.jsx
    ├── CommonPersonalizationPage.jsx
    └── CommonPromptPage.jsx
```

### Common Components
Format: `{ComponentName}.jsx`

```
components/
└── common/
    ├── Button.jsx
    ├── Card.jsx
    ├── PageHeader.jsx
    ├── PageLayout.jsx
    └── FooterButtons.jsx
```

## Vorteile

✅ **Konsistente Patterns:**
```
Backend Python:    audio_feedback_plugin.py  (snake_case)
Frontend React:    AudioFeedbackUploadPage   (PascalCase)
Dokumentation:     AudioFeedbackTemplates.md (PascalCase)
```

✅ **Sprachspezifische Konventionen:**
```
Python:      snake_case     → audio_feedback_service.py
JavaScript:  PascalCase     → AudioFeedbackUploadPage.jsx
Ordner:      kebab-case     → audio-feedback/
```

✅ **VS Code Tabs sofort erkennbar:**
```
[audio_feedback_plugin.py] [midi_comparison_service.py]
  ↑ Audio Plugin               ↑ MIDI Service
```

✅ **Dateisuche eindeutig:**
```
Strg+P: "audio_feedback_" → Zeigt alle Audio-Feedback-Dateien
Strg+P: "AudioFeedback" → Zeigt alle Audio-Feedback-Components
```

✅ **Keine Verwirrung mehr:**
```
❌ ALT: [plugin.py] [service.py] [routes.py] - Welches ist welches?
✅ NEU: [audio_feedback_plugin.py] [midi_comparison_service.py] - Sofort klar!
```

## Beispiele für neue Plugins

Wenn du ein neues Plugin erstellst, folge dem Muster:

```python
# Backend
plugins/
└── {new_tool}/
    ├── {new_tool}_plugin.py
    ├── {new_tool}_service.py
    ├── {new_tool}_routes.py
    └── templates/
        └── {NewTool}Templates.md

# Frontend
pages/
└── {new-tool}/
    ├── {NewTool}UploadPage.jsx
    ├── {NewTool}SettingsPage.jsx
    └── {NewTool}ResultsPage.jsx
```

## Plugin Manager

Der Plugin Manager lädt automatisch: `{plugin_name}_plugin.py`

```python
# In plugin_manager.py
module_path = f'app.plugins.{plugin_module}.{plugin_module}_plugin'
```

# MuDiKo Musik-Assistent Chatbot – Konzept & Architektur

> **Version:** 1.0 (Entwurf)  
> **Datum:** Januar 2026  
> **Status:** Konzeptphase

---

## 1. Vision & Zielsetzung

### 1.1 Das Problem

Die aktuelle MuDiKo-Oberfläche bietet drei spezialisierte Tools:
- **Audio-Feedback:** Vergleicht Schüler- mit Referenzaufnahmen
- **MIDI-Vergleich:** Analysiert MIDI-Dateien taktgenau
- **MP3-zu-MIDI:** Konvertiert Audioaufnahmen in MIDI-Format

Schüler müssen:
1. Das richtige Tool selbst auswählen
2. Die korrekten Dateien hochladen
3. Mehrere Konfigurationsschritte durchlaufen
4. Den generierten Prompt manuell in ein LLM kopieren

Dies erfordert technisches Verständnis und unterbricht den Lernfluss.

### 1.2 Die Lösung: Musik-Assistent

Ein **Chatbot als einheitliche Schnittstelle**, die:
- Natürliche Sprache versteht ("Wie war meine Aufnahme?")
- Automatisch das passende Tool auswählt und ausführt
- Ergebnisse in verständlicher, pädagogisch wertvoller Form präsentiert
- Den gesamten Workflow in einer Konversation bündelt

### 1.3 Kernprinzip: "Smart Proxy"

Da die Schul-LLM-API eingeschränkt ist (Token-Limit, vordefinierte System-Prompts), verlagern wir die Intelligenz ins Backend:

```
┌─────────────────────────────────────────────────────────┐
│                    INTELLIGENZ-VERTEILUNG               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   LOKAL (Backend)              │   LLM (Schul-API)     │
│   ─────────────────            │   ────────────────     │
│   • Intent-Erkennung           │   • Natürliche        │
│   • Tool-Auswahl               │     Formulierung      │
│   • Audio/MIDI-Analyse         │   • Pädagogischer     │
│   • Daten-Kompression          │     Tonfall           │
│   • Visualisierungen           │   • Motivation        │
│   • Kontext-Management         │   • Erklärungen       │
│                                │                        │
│   → 80% der Arbeit             │   → 20% "Veredelung"  │
│   → 0 Tokens                   │   → ~200-500 Tokens   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Architektur

### 2.1 Systemübersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Chat-Interface                           │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ 💬 Chatbot                                            │  │ │
│  │  │                                                       │  │ │
│  │  │ 🤖 Hallo! Ich bin dein Musik-Assistent.              │  │ │
│  │  │    Was möchtest du heute üben?                       │  │ │
│  │  │                                                       │  │ │
│  │  │ 👤 Ich habe gerade "Für Elise" auf dem Klavier       │  │ │
│  │  │    geübt. Kannst du mir sagen wie es war?            │  │ │
│  │  │    📎 meine_aufnahme.mp3                             │  │ │
│  │  │                                                       │  │ │
│  │  │ 🤖 [Analyse läuft...]                                │  │ │
│  │  │    ┌─────────────────────────────────┐               │  │ │
│  │  │    │ 🎹 Tempo: 72 BPM (Ziel: 70)    │               │  │ │
│  │  │    │ 🎵 Rhythmus: 87% Genauigkeit   │               │  │ │
│  │  │    │ 📊 [Wellenform-Visualisierung] │               │  │ │
│  │  │    └─────────────────────────────────┘               │  │ │
│  │  │    Das klingt schon richtig gut! Dein Tempo ist     │  │ │
│  │  │    sehr stabil. In Takt 12-14 könntest du die       │  │ │
│  │  │    Übergänge noch etwas weicher spielen...          │  │ │
│  │  │                                                       │  │ │
│  │  │ ┌─────────────────────────────────────────────────┐  │ │
│  │  │ │ 📎 Datei anhängen   [Nachricht eingeben...]  ➤ │  │ │
│  │  │ └─────────────────────────────────────────────────┘  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────┐  ← Optional: Direktzugang zu Tools     │
│  │ 🛠️ Erweiterte Tools │     für Power-User                     │
│  └─────────────────────┘                                         │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                          BACKEND                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    CHATBOT-PLUGIN                            │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │ │
│  │  │   Intent-    │  │   Prompt-    │  │   Conversation   │   │ │
│  │  │   Detector   │  │   Builder    │  │   Manager        │   │ │
│  │  │              │  │              │  │                  │   │ │
│  │  │ • Regex      │  │ • Kompri-    │  │ • Chat-Historie  │   │ │
│  │  │ • Keywords   │  │   mierung    │  │ • Kontext        │   │ │
│  │  │ • Datei-     │  │ • Template-  │  │ • Session-       │   │ │
│  │  │   erkennung  │  │   System     │  │   Verwaltung     │   │ │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │ │
│  │         │                 │                   │              │ │
│  │         └────────────┬────┴───────────────────┘              │ │
│  │                      │                                       │ │
│  │                      ▼                                       │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │              TOOL ORCHESTRATOR                        │   │ │
│  │  │                                                       │   │ │
│  │  │   Wählt und führt das passende Tool aus:             │   │ │
│  │  │                                                       │   │ │
│  │  │   ┌─────────────┐ ┌─────────────┐ ┌───────────────┐  │   │ │
│  │  │   │   Audio-    │ │   MIDI-     │ │  MP3-to-MIDI  │  │   │ │
│  │  │   │  Feedback   │ │  Vergleich  │ │  Konverter    │  │   │ │
│  │  │   │  Service    │ │  Service    │ │  Service      │  │   │ │
│  │  │   └─────────────┘ └─────────────┘ └───────────────┘  │   │ │
│  │  │                                                       │   │ │
│  │  │   + Zukünftige Tools:                                │   │ │
│  │  │   • Akkord-Erkennung                                  │   │ │
│  │  │   • Tonleiter-Trainer                                 │   │ │
│  │  │   • Gehörbildung                                      │   │ │
│  │  │   • ...                                               │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                      │                                       │ │
│  │                      ▼                                       │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │              LLM GATEWAY                              │   │ │
│  │  │                                                       │   │ │
│  │  │   • Sendet komprimierten Kontext an Schul-API        │   │ │
│  │  │   • Empfängt pädagogisch formulierte Antwort         │   │ │
│  │  │   • Fallback bei Fehler/Timeout                      │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 SHARED SERVICES (bestehend)                  │ │
│  │   SessionService │ StorageService │ AudioService │ ...      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │      SCHUL-LLM-API        │
                    │                           │
                    │  • DSGVO-konform          │
                    │  • Token-limitiert        │
                    │  • Pädagogische Prompts   │
                    └───────────────────────────┘
```

### 2.2 Komponenten-Details

#### 2.2.1 Intent Detector

Erkennt die Benutzerabsicht **ohne LLM-Aufruf** durch:

```python
class IntentDetector:
    """
    Regelbasierte Intent-Erkennung für Token-Effizienz.
    Kein LLM-Aufruf nötig.
    """
    
    INTENT_PATTERNS = {
        'audio_feedback': {
            'keywords': ['aufnahme', 'gespielt', 'geübt', 'anhören', 
                        'feedback', 'wie war', 'wie klang'],
            'file_types': ['.mp3', '.wav', '.m4a', '.ogg'],
            'requires_files': True
        },
        'midi_comparison': {
            'keywords': ['midi', 'noten', 'partitur', 'vergleich', 
                        'richtig gespielt'],
            'file_types': ['.mid', '.midi'],
            'requires_files': True
        },
        'mp3_to_midi': {
            'keywords': ['konvertier', 'umwandeln', 'zu midi', 
                        'noten erstellen', 'transkribier'],
            'file_types': ['.mp3', '.wav'],
            'requires_files': True
        },
        'general_music_question': {
            'keywords': ['was ist', 'erkläre', 'wie funktioniert',
                        'musiktheorie', 'akkord', 'tonleiter'],
            'requires_files': False
        },
        'greeting': {
            'keywords': ['hallo', 'hi', 'hey', 'guten tag'],
            'requires_files': False
        }
    }
    
    def detect(self, message: str, attachments: List[str]) -> Intent:
        # 1. Datei-basierte Erkennung (höchste Priorität)
        if attachments:
            intent = self._detect_by_files(attachments)
            if intent:
                return intent
        
        # 2. Keyword-basierte Erkennung
        return self._detect_by_keywords(message)
```

**Erweiterbarkeit:** Neue Intents können einfach durch Hinzufügen von Patterns registriert werden – ohne LLM-Anpassungen.

#### 2.2.2 Tool Orchestrator

Führt das erkannte Tool aus und sammelt Analyse-Daten:

```python
class ToolOrchestrator:
    """
    Verbindet Intent mit dem passenden Plugin-Service.
    """
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugins = plugin_manager
        
        # Mapping: Intent → Plugin + Methode
        self.tool_mapping = {
            'audio_feedback': {
                'plugin': 'audio-feedback',
                'method': 'analyze_audio',
                'required_params': ['audio_file']
            },
            'midi_comparison': {
                'plugin': 'midi-comparison', 
                'method': 'compare_midi',
                'required_params': ['reference_file', 'student_file']
            },
            'mp3_to_midi': {
                'plugin': 'mp3-to-midi-feedback',
                'method': 'convert',
                'required_params': ['audio_file']
            }
        }
    
    async def execute(self, intent: str, context: ChatContext) -> ToolResult:
        """
        Führt Tool aus und gibt strukturierte Ergebnisse zurück.
        """
        tool_config = self.tool_mapping[intent]
        plugin = self.plugins.get_plugin(tool_config['plugin'])
        
        # Sammle Parameter aus Kontext
        params = self._extract_params(context, tool_config)
        
        # Führe Analyse aus
        result = await plugin.service.execute(params)
        
        return ToolResult(
            success=True,
            data=result.analysis_data,      # Für Prompt-Builder
            visualizations=result.charts,    # Für Frontend
            raw_output=result.raw            # Für Debugging
        )
```

#### 2.2.3 Prompt Builder (Kompression)

Transformiert detaillierte Analyse-Daten in token-effiziente Prompts:

```python
class PromptBuilder:
    """
    Komprimiert Analyse-Ergebnisse für die token-limitierte Schul-API.
    Ziel: Maximale Information bei minimalen Tokens.
    """
    
    def build_prompt(
        self, 
        intent: str,
        user_message: str,
        tool_result: ToolResult,
        conversation_context: List[Message]
    ) -> str:
        """
        Baut einen kompakten Prompt für die Schul-API.
        """
        
        # Basis-Template laden
        template = self._load_template(intent)
        
        # Analyse-Daten komprimieren
        compressed_data = self._compress_analysis(tool_result.data)
        
        # Konversations-Kontext (letzte 2-3 Nachrichten)
        recent_context = self._summarize_context(conversation_context[-3:])
        
        return template.format(
            user_input=user_message,
            analysis=compressed_data,
            context=recent_context,
            instrument=tool_result.data.get('instrument', 'Instrument')
        )
    
    def _compress_analysis(self, data: dict) -> str:
        """
        Beispiel-Kompression:
        
        INPUT (detailliert):
        {
            "overall_similarity": 0.78,
            "tempo": {"detected": 92, "reference": 90, "deviation": 2.2},
            "rhythm": {"accuracy": 0.85, "issues": [
                {"bar": 3, "beat": 2, "type": "rushed"},
                {"bar": 7, "beat": 1, "type": "delayed"}
            ]},
            "pitch": {"accuracy": 0.92, "issues": []},
            "dynamics": {"variance": 0.3, "rating": "good"}
        }
        
        OUTPUT (komprimiert, ~50 Tokens):
        "Ähnlichkeit: 78%. Tempo: 92 BPM (Ziel 90, gut). 
         Rhythmus: 85% (Takt 3+7 ungenau). Tonhöhe: 92% (sehr gut).
         Dynamik: Gute Variation."
        """
        lines = []
        
        if 'overall_similarity' in data:
            lines.append(f"Ähnlichkeit: {int(data['overall_similarity']*100)}%")
        
        if 'tempo' in data:
            t = data['tempo']
            lines.append(f"Tempo: {t['detected']} BPM (Ziel {t['reference']})")
        
        if 'rhythm' in data:
            r = data['rhythm']
            acc = int(r['accuracy'] * 100)
            issues = [f"T{i['bar']}" for i in r['issues'][:3]]
            issue_str = f" (Probleme: {', '.join(issues)})" if issues else ""
            lines.append(f"Rhythmus: {acc}%{issue_str}")
        
        # ... weitere Kompression
        
        return " | ".join(lines)
```

**Beispiel-Prompts für verschiedene Intents:**

```
# Audio-Feedback (mit Referenz)
"Musikfeedback für Klavier-Aufnahme von 'Für Elise'.
Analyse: Ähnlichkeit 78% | Tempo 92 BPM (Ziel 90) | Rhythmus 85% (T3, T7 ungenau) | Tonhöhe 92%
Schüler fragt: 'Wie war meine Aufnahme?'
Gib kurzes, ermutigendes Feedback (3-4 Sätze). Nenne konkrete Verbesserungen."

# MIDI-Vergleich  
"MIDI-Vergleich für Gitarren-Übung.
Analyse: 45 von 52 Noten korrekt | Takt 5-6: falsche Noten (E statt F) | Timing: gut
Schüler fragt: 'Welche Fehler habe ich gemacht?'
Erkläre die Fehler verständlich und gib Übungstipps."

# Allgemeine Musikfrage (kein Tool nötig)
"Schüler fragt: 'Was ist ein Akkord?'
Erkläre kindgerecht in 2-3 Sätzen."
```

#### 2.2.4 Conversation Manager

Verwaltet Chat-Historie und Kontext:

```python
class ConversationManager:
    """
    Speichert Chat-Verlauf und ermöglicht Kontext-bezogene Antworten.
    """
    
    def __init__(self, session_service: SessionService):
        self.sessions = session_service
    
    async def add_message(
        self, 
        session_id: str, 
        role: str,  # 'user' | 'assistant'
        content: str,
        metadata: dict = None
    ):
        """Fügt Nachricht zur Historie hinzu."""
        session = await self.sessions.get(session_id)
        session.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata  # z.B. verwendetes Tool, Dateien
        })
    
    def get_context_summary(self, session_id: str, max_messages: int = 5) -> str:
        """
        Erstellt kompakte Zusammenfassung für Follow-up-Fragen.
        
        Beispiel:
        "Vorheriger Kontext: Schüler hat Klavier-Aufnahme von 'Für Elise' 
         analysieren lassen. Ergebnis: 78% Ähnlichkeit, Rhythmusprobleme in T3+T7."
        """
        session = self.sessions.get(session_id)
        recent = session.messages[-max_messages:]
        
        # Komprimiere zu ~50 Tokens
        return self._summarize_messages(recent)
```

#### 2.2.5 LLM Gateway

Schnittstelle zur Schul-API:

```python
class LLMGateway:
    """
    Einfache Text-in/Text-out Schnittstelle zur Schul-LLM-API.
    """
    
    def __init__(self, config: dict):
        self.api_url = config['school_llm_api_url']
        self.api_key = config.get('api_key')  # Falls benötigt
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 2)
    
    async def generate(self, prompt: str) -> LLMResponse:
        """
        Sendet Prompt an Schul-API und empfängt Antwort.
        """
        try:
            response = await self._call_api(prompt)
            return LLMResponse(
                success=True,
                text=response['text'],
                tokens_used=response.get('tokens_used')
            )
        except TokenLimitExceeded:
            # Prompt war zu lang → verkürzen und retry
            shortened = self._shorten_prompt(prompt)
            return await self.generate(shortened)
        except APIError as e:
            return LLMResponse(
                success=False,
                error=str(e),
                fallback_text=self._get_fallback_response()
            )
    
    def _shorten_prompt(self, prompt: str) -> str:
        """Entfernt optionale Kontext-Teile wenn Token-Limit erreicht."""
        # Strategie: Konversations-Kontext entfernen, nur aktuelle Analyse
        # ...
```

---

## 3. Feature-Katalog

### 3.1 Kern-Features (MVP)

| Feature | Beschreibung | Priorität |
|---------|--------------|-----------|
| **Chat-Interface** | Einfache Konversations-UI mit Nachrichten-History | 🔴 Hoch |
| **Datei-Upload im Chat** | Drag & Drop oder Klick für Audio/MIDI-Dateien | 🔴 Hoch |
| **Automatische Tool-Erkennung** | Intent-Detection wählt passendes Tool | 🔴 Hoch |
| **Inline-Visualisierungen** | Analyse-Charts direkt im Chat anzeigen | 🔴 Hoch |
| **Audio-Playback im Chat** | Hochgeladene Dateien können abgespielt werden | 🔴 Hoch |
| **Einfache Follow-ups** | "Kannst du das genauer erklären?" funktioniert | 🟡 Mittel |

### 3.2 Erweiterte Features (Phase 2)

| Feature | Beschreibung | Priorität |
|---------|--------------|-----------|
| **Referenz-Bibliothek** | Vorgefertigte Referenzstücke zum Üben | 🟡 Mittel |
| **Übungsvorschläge** | Basierend auf erkannten Schwächen | 🟡 Mittel |
| **Vergleich mit vorheriger Aufnahme** | "War das besser als gestern?" | 🟡 Mittel |
| **Multi-Turn-Analyse** | Mehrere Aufnahmen in einer Session vergleichen | 🟡 Mittel |
| **Schnellaktionen** | Buttons wie "Nochmal analysieren", "Andere Datei" | 🟡 Mittel |

### 3.3 Zukunfts-Features (Phase 3+)

| Feature | Beschreibung | Priorität |
|---------|--------------|-----------|
| **Lernfortschritt-Dashboard** | Visualisiert Entwicklung über Zeit | 🟢 Niedrig |
| **Übungspläne generieren** | Personalisierte Wochenübungen | 🟢 Niedrig |
| **Gehörbildungs-Modus** | Intervalle, Akkorde erkennen | 🟢 Niedrig |
| **Metronom-Integration** | Im Chat steuerbares Metronom | 🟢 Niedrig |
| **Kollaboration** | Lehrer kann Chat-Verlauf einsehen | 🟢 Niedrig |

---

## 4. Benutzer-Flows

### 4.1 Hauptflow: Audio-Feedback

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIO-FEEDBACK FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Schüler: "Ich habe gerade Klavier geübt, hör mal!"
         📎 meine_aufnahme.mp3
                │
                ▼
┌─────────────────────────────────────────┐
│ Intent Detector                          │
│ → Erkennt: Audio-Datei + "geübt"        │
│ → Intent: audio_feedback                 │
│ → Modus: ohne Referenz (einfache        │
│          Analyse)                        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Tool Orchestrator                        │
│ → Ruft AudioFeedbackService auf         │
│ → Analysiert: Tempo, Rhythmus, Tonhöhe  │
│ → Ergebnis: {tempo: 92, rhythm: 0.85}   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Prompt Builder                           │
│ → Komprimiert Analyse                   │
│ → Erstellt: "Klavier-Aufnahme.          │
│   Tempo 92 BPM, Rhythmus 85%.           │
│   Gib ermutigendes Feedback."           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ LLM Gateway (Schul-API)                  │
│ → Sendet kompakten Prompt               │
│ → Empfängt: "Das klingt schon toll!     │
│   Dein Tempo ist sehr stabil..."        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Response Builder                         │
│ → Kombiniert LLM-Text + Visualisierung  │
└────────────────┬────────────────────────┘
                 │
                 ▼
Assistent: ┌─────────────────────────────────────┐
           │ 🎹 Analyse deiner Aufnahme:         │
           │ ├─ Tempo: 92 BPM ✓                  │
           │ ├─ Rhythmus: 85% ⚠️                  │
           │ └─ [▶️ Wellenform-Visualisierung]   │
           │                                      │
           │ Das klingt schon toll! Dein Tempo   │
           │ ist sehr stabil. Achte in Takt 3    │
           │ auf den Übergang – da eilst du      │
           │ etwas. Versuch es langsamer zu      │
           │ üben und steigere dann das Tempo.   │
           │                                      │
           │ [🔄 Nochmal analysieren]            │
           │ [📎 Mit Referenz vergleichen]       │
           └─────────────────────────────────────┘
```

### 4.2 Follow-up Flow

```
Schüler: "Was meinst du mit 'Übergang in Takt 3'?"
                │
                ▼
┌─────────────────────────────────────────┐
│ Intent Detector                          │
│ → Keine Datei, Frageformulierung        │
│ → Intent: follow_up_question            │
│ → Kontext: vorherige Audio-Analyse      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Conversation Manager                     │
│ → Holt Kontext: "Klavier, Rhythmus 85%, │
│   Problem Takt 3"                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Prompt Builder                           │
│ → "Kontext: Schüler hat Klavier geübt,  │
│   Rhythmusproblem in Takt 3.            │
│   Frage: Was ist der Übergang?          │
│   Erkläre kindgerecht."                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
Assistent: "In Takt 3 wechselt die Melodie von den 
            hohen zu den tiefen Tönen. Dieser Wechsel 
            heißt 'Übergang'. Bei dir war dieser Moment 
            etwas schneller als der Rest. Tipp: Zähle 
            dort bewusst '1-2-3-4' mit."
```

### 4.3 Multi-File Flow (MIDI-Vergleich)

```
Schüler: "Kannst du meine Version mit dem Original vergleichen?"
         📎 original.mid
         📎 meine_version.mid
                │
                ▼
┌─────────────────────────────────────────┐
│ Intent Detector                          │
│ → 2x MIDI-Dateien + "vergleichen"       │
│ → Intent: midi_comparison               │
│ → Params: reference=original.mid,       │
│           student=meine_version.mid     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Tool Orchestrator                        │
│ → Ruft MidiComparisonService auf        │
│ → Taktweiser Vergleich                  │
│ → Ergebnis: 45/52 Noten korrekt,        │
│   Fehler in Takt 5-6                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
Assistent: ┌─────────────────────────────────────┐
           │ 📊 MIDI-Vergleich:                  │
           │                                      │
           │ Takt │ Original │ Deine Version     │
           │ ─────┼──────────┼─────────────────  │
           │  1-4 │ ✓        │ ✓ Perfekt!        │
           │  5   │ F-A-C    │ E-A-C ⚠️ (1.Note) │
           │  6   │ G-B-D    │ G-B-D ✓           │
           │ 7-12 │ ✓        │ ✓ Perfekt!        │
           │                                      │
           │ Super gemacht! Fast alle Noten      │
           │ stimmen. In Takt 5 spielst du ein   │
           │ E statt F – das ist nur ein         │
           │ Halbton Unterschied. Schau dir      │
           │ die Stelle nochmal langsam an.      │
           └─────────────────────────────────────┘
```

---

## 5. API-Design

### 5.1 Chat-Endpoint

```
POST /api/tools/chatbot/chat
```

**Request:**
```json
{
    "sessionId": "sess_abc123",
    "message": "Wie war meine Aufnahme?",
    "attachments": [
        {
            "filename": "meine_aufnahme.mp3",
            "fileId": "file_xyz789"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "response": {
        "text": "Das klingt schon richtig gut! Dein Tempo ist sehr stabil...",
        "visualizations": [
            {
                "type": "audio_waveform",
                "data": { "peaks": [...], "duration": 45.2 }
            },
            {
                "type": "metrics_card",
                "data": {
                    "tempo": { "value": 92, "unit": "BPM", "status": "good" },
                    "rhythm": { "value": 85, "unit": "%", "status": "warning" }
                }
            }
        ],
        "suggestions": [
            { "text": "Nochmal analysieren", "action": "reanalyze" },
            { "text": "Mit Referenz vergleichen", "action": "add_reference" }
        ],
        "toolUsed": "audio-feedback"
    },
    "conversationId": "conv_def456"
}
```

### 5.2 Datei-Upload

```
POST /api/tools/chatbot/upload
```

**Request:** (multipart/form-data)
- `file`: Die Datei
- `sessionId`: Session-ID

**Response:**
```json
{
    "success": true,
    "fileId": "file_xyz789",
    "filename": "meine_aufnahme.mp3",
    "mimeType": "audio/mpeg",
    "duration": 45.2,
    "canPreview": true
}
```

### 5.3 Chat-Historie

```
GET /api/tools/chatbot/history?sessionId=sess_abc123
```

**Response:**
```json
{
    "sessionId": "sess_abc123",
    "messages": [
        {
            "id": "msg_001",
            "role": "assistant",
            "content": "Hallo! Ich bin dein Musik-Assistent...",
            "timestamp": "2026-01-05T10:00:00Z"
        },
        {
            "id": "msg_002", 
            "role": "user",
            "content": "Wie war meine Aufnahme?",
            "attachments": [{ "filename": "meine_aufnahme.mp3" }],
            "timestamp": "2026-01-05T10:01:00Z"
        }
    ]
}
```

---

## 6. Frontend-Komponenten

### 6.1 Komponenten-Hierarchie

```
ChatPage/
├── ChatHeader/
│   ├── Logo
│   ├── SessionInfo
│   └── NewChatButton
│
├── ChatMessages/
│   ├── MessageList/
│   │   ├── UserMessage/
│   │   │   ├── MessageContent
│   │   │   └── AttachmentPreview
│   │   │
│   │   └── AssistantMessage/
│   │       ├── MessageContent
│   │       ├── VisualizationCard/
│   │       │   ├── AudioWaveform
│   │       │   ├── MetricsDisplay
│   │       │   ├── MidiComparison
│   │       │   └── AudioPlayer
│   │       └── SuggestionButtons
│   │
│   └── TypingIndicator
│
├── ChatInput/
│   ├── AttachmentButton
│   ├── AttachmentPreviewList
│   ├── TextInput
│   └── SendButton
│
└── AttachmentDropzone (overlay)
```

### 6.2 Schlüssel-Komponenten

#### ChatMessages (Beispiel)

```jsx
function ChatMessages({ messages, isLoading }) {
    return (
        <div className="chat-messages">
            {messages.map(msg => (
                msg.role === 'user' 
                    ? <UserMessage key={msg.id} message={msg} />
                    : <AssistantMessage key={msg.id} message={msg} />
            ))}
            
            {isLoading && <TypingIndicator />}
        </div>
    );
}

function AssistantMessage({ message }) {
    return (
        <div className="assistant-message">
            <div className="message-content">
                {message.text}
            </div>
            
            {/* Visualisierungen inline anzeigen */}
            {message.visualizations?.map((viz, i) => (
                <VisualizationCard key={i} type={viz.type} data={viz.data} />
            ))}
            
            {/* Schnellaktionen */}
            {message.suggestions?.length > 0 && (
                <div className="suggestions">
                    {message.suggestions.map((sug, i) => (
                        <SuggestionButton key={i} {...sug} />
                    ))}
                </div>
            )}
        </div>
    );
}
```

#### VisualizationCard (Beispiel)

```jsx
function VisualizationCard({ type, data }) {
    const components = {
        'audio_waveform': AudioWaveform,
        'metrics_card': MetricsDisplay,
        'midi_comparison': MidiComparisonTable,
        'audio_player': AudioPlayer
    };
    
    const Component = components[type];
    
    return (
        <div className="visualization-card">
            <Component data={data} />
        </div>
    );
}

function MetricsDisplay({ data }) {
    return (
        <div className="metrics-grid">
            {Object.entries(data).map(([key, metric]) => (
                <div key={key} className={`metric ${metric.status}`}>
                    <span className="label">{key}</span>
                    <span className="value">{metric.value} {metric.unit}</span>
                    <StatusIcon status={metric.status} />
                </div>
            ))}
        </div>
    );
}
```

---

## 7. Token-Optimierungs-Strategien

Da die Schul-API token-limitiert ist, sind folgende Strategien wichtig:

### 7.1 Prompt-Längen-Budget

```
┌─────────────────────────────────────────────────────────────┐
│              TYPISCHES TOKEN-BUDGET (~500 Tokens)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Aufgaben-Beschreibung    │  ~50 Tokens                    │
│  "Gib Feedback für eine Klavier-Aufnahme..."               │
│                                                             │
│  Komprimierte Analyse     │  ~100 Tokens                   │
│  "Tempo 92 BPM | Rhythmus 85% (T3 ungenau) | Tonhöhe 92%"  │
│                                                             │
│  Konversations-Kontext    │  ~50 Tokens (optional)         │
│  "Vorher: Schüler fragte nach Rhythmus-Tipps"              │
│                                                             │
│  User-Nachricht           │  ~50 Tokens                    │
│  "Wie war meine Aufnahme?"                                  │
│                                                             │
│  Antwort-Anweisungen      │  ~30 Tokens                    │
│  "Antworte in 3-4 Sätzen, ermutigend, mit konkretem Tipp." │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  GESAMT INPUT:            │  ~280 Tokens                   │
│  RESERVE FÜR OUTPUT:      │  ~220 Tokens                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Komprimierungs-Techniken

| Technik | Vorher | Nachher | Ersparnis |
|---------|--------|---------|-----------|
| **Zahlen-Rundung** | "87.3456%" | "87%" | ~3 Tokens |
| **Abkürzungen** | "Takt" | "T" | ~1 Token |
| **Listen-Kompression** | "Takt 3, Takt 5, Takt 7" | "T3,5,7" | ~4 Tokens |
| **Status-Symbole** | "ist in Ordnung" | "✓" | ~3 Tokens |
| **Kontext-Weglassen** | Volle Historie | Letzte 2 Nachrichten | ~100 Tokens |

### 7.3 Caching-Strategie

```python
class ResponseCache:
    """
    Cached LLM-Antworten für ähnliche Analyse-Ergebnisse.
    Spart Tokens bei wiederkehrenden Mustern.
    """
    
    def get_cache_key(self, intent: str, metrics: dict) -> str:
        """
        Gruppiert ähnliche Ergebnisse.
        
        Beispiel: Rhythmus 83% und 87% → gleicher Cache-Key "rhythm_80-90"
        """
        buckets = {
            'rhythm': self._bucket(metrics.get('rhythm', 0), step=10),
            'tempo_deviation': self._bucket(metrics.get('tempo_dev', 0), step=5),
            'overall': self._bucket(metrics.get('overall', 0), step=10)
        }
        return f"{intent}_{buckets}"
    
    def _bucket(self, value: float, step: int) -> str:
        lower = int(value // step) * step
        return f"{lower}-{lower + step}"
```

---

## 8. Fehlerbehandlung

### 8.1 Fehler-Szenarien

| Szenario | Ursache | Lösung |
|----------|---------|--------|
| **API-Timeout** | Schul-API antwortet nicht | Lokale Fallback-Nachricht |
| **Token-Limit überschritten** | Prompt zu lang | Kontext kürzen, Retry |
| **Unbekannte Datei** | Nicht unterstütztes Format | Freundliche Fehlermeldung |
| **Analyse fehlgeschlagen** | Datei korrupt/zu kurz | Erklärung + Handlungsempfehlung |
| **Kein Intent erkannt** | Unklare Anfrage | Rückfrage stellen |

### 8.2 Fallback-Antworten

```python
FALLBACK_RESPONSES = {
    'api_error': """
        Entschuldige, ich konnte gerade nicht richtig antworten. 
        Hier ist was ich herausgefunden habe:
        
        {analysis_summary}
        
        Versuch es gleich nochmal, dann kann ich dir 
        ausführlicheres Feedback geben!
    """,
    
    'unknown_intent': """
        Hmm, ich bin mir nicht sicher was du meinst. 
        Ich kann dir helfen mit:
        
        🎵 Audio-Aufnahmen analysieren
        🎹 MIDI-Dateien vergleichen  
        🔄 Audio zu MIDI umwandeln
        
        Schick mir einfach eine Datei oder beschreib 
        was du üben möchtest!
    """,
    
    'unsupported_file': """
        Diese Datei kann ich leider nicht verarbeiten.
        Unterstützte Formate:
        
        🎵 Audio: MP3, WAV, M4A, OGG
        🎹 MIDI: MID, MIDI
        
        Versuch es mit einem anderen Format!
    """
}
```

---

## 9. Implementierungs-Roadmap

### Phase 1: Fundament (2-3 Wochen)

- [ ] **Backend: Chatbot-Plugin Grundstruktur**
  - Plugin-Klasse nach bestehendem Muster
  - Einfacher `/chat` Endpoint
  - Session-Integration

- [ ] **Backend: LLM Gateway**
  - Schul-API Anbindung
  - Request/Response Handling
  - Basis-Fehlerbehandlung

- [ ] **Backend: Intent Detector v1**
  - Keyword-basierte Erkennung
  - Dateiendungs-Erkennung
  - Mapping zu bestehenden Tools

- [ ] **Frontend: Chat-UI Grundstruktur**
  - Message-Liste
  - Text-Input
  - Einfaches Styling

### Phase 2: Tool-Integration (2-3 Wochen)

- [ ] **Backend: Tool Orchestrator**
  - Integration mit Audio-Feedback-Service
  - Integration mit MIDI-Comparison-Service
  - Integration mit MP3-to-MIDI-Service

- [ ] **Backend: Prompt Builder**
  - Analyse-Kompression
  - Template-System
  - Kontext-Zusammenfassung

- [ ] **Frontend: Datei-Upload**
  - Drag & Drop
  - Attachment-Preview
  - Upload-Progress

- [ ] **Frontend: Visualisierungen**
  - Metrics-Cards
  - Bestehende Visualisierungen einbinden

### Phase 3: Polish & Features (2 Wochen)

- [ ] **Backend: Conversation Manager**
  - Chat-Historie speichern
  - Follow-up Kontext
  - Session-Cleanup

- [ ] **Backend: Fehlerbehandlung**
  - Fallback-Responses
  - Token-Limit-Handling
  - Retry-Logik

- [ ] **Frontend: UX-Verbesserungen**
  - Typing-Indicator
  - Suggestion-Buttons
  - Audio-Player im Chat
  - Responsive Design

- [ ] **Testing & Dokumentation**
  - Integration-Tests
  - API-Dokumentation
  - Benutzer-Anleitung

---

## 10. Offene Fragen

1. **Schul-API Details:**
   - Wie sieht der genaue API-Endpunkt aus?
   - Gibt es Authentifizierung (API-Key, Token)?
   - Was ist das genaue Token-Limit?
   - Gibt es Rate-Limiting?

2. **Pädagogische Ausrichtung:**
   - Welche Altersgruppe ist die Zielgruppe?
   - Sollen verschiedene Schwierigkeitsstufen erkennbar sein?
   - Gibt es spezielle pädagogische Anforderungen?

3. **Datenschutz:**
   - Wie lange dürfen Chat-Verläufe gespeichert werden?
   - Sollen Aufnahmen nach Analyse gelöscht werden?
   - Gibt es Logging-Anforderungen?

4. **Deployment:**
   - Bleibt das Docker-Setup bestehen?
   - Gibt es Performance-Anforderungen (max. Antwortzeit)?

---

## 11. Anhang: Bestehende Architektur-Integration

Das Chatbot-Plugin fügt sich nahtlos in die bestehende Plugin-Architektur ein:

```
Backend/app/plugins/
├── base/
│   ├── plugin_interface.py  ← Chatbot implementiert dieses Interface
│   └── plugin_manager.py    ← Registriert Chatbot automatisch
│
├── audio_feedback/          ← Wird vom Chatbot orchestriert
├── midi_comparison/         ← Wird vom Chatbot orchestriert
├── mp3_to_midi_feedback/    ← Wird vom Chatbot orchestriert
│
└── chatbot/                 ← NEU
    ├── __init__.py
    ├── chatbot_plugin.py
    ├── chatbot_routes.py
    ├── chatbot_service.py
    ├── intent_detector.py
    ├── tool_orchestrator.py
    ├── prompt_builder.py
    ├── conversation_manager.py
    ├── llm_gateway.py
    ├── config.yaml
    └── templates/
        └── prompts/
            ├── audio_feedback.txt
            ├── midi_comparison.txt
            └── general_question.txt
```

Die bestehenden Shared Services werden vollständig wiederverwendet:
- `SessionService` → Chat-Sessions
- `StorageService` → Datei-Uploads
- `AudioService` → Audio-Verarbeitung
- `PromptTemplateLoader` → Template-System

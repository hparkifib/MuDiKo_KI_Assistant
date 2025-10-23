# LLM Test-Modus Setup 🧪

## ✅ Test-Modus ist jetzt aktiv!

Der LLM Feedback Prototyp läuft jetzt im **Test-Modus** ohne echte API Keys. Das System erkennt automatisch, dass keine gültigen API Keys vorhanden sind und aktiviert Demo-Responses.

## 🔍 Status Prüfen

**Backend Status:**
```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:5000/api/llm/status
```

**Erwartete Antwort:**
```json
{
  "llmAvailable": false,
  "message": "🧪 Test-Modus aktiv - Demo-Responses", 
  "model": "gpt-4o-mini",
  "provider": "openai",
  "status": "test-mode",
  "testMode": true
}
```

## 🎯 Was der Test-Modus bietet

### Frontend (LLMFeedbackPrototype.jsx)
- ✅ "🧪 Test-Modus" Anzeige im Header
- ✅ Vollständige UI-Funktionalität 
- ✅ Realistische Mock-Responses für alle Segmente
- ✅ Chat-System funktioniert komplett
- ✅ Keine API-Kosten

### Backend (llm_service.py)
- ✅ Automatische Erkennung von Beispiel-Keys (`your_openai_api_key_here`)
- ✅ Realistische Demo-Responses mit `🧪 [TEST-MODUS]` Prefix
- ✅ Alle LLM Endpoints funktionieren (`/api/llm/feedback`, `/api/llm/status`)
- ✅ Fallback zu Mock-Data bei jedem API Call

## 🚀 Testen im Browser

1. **Öffne die App:** http://localhost oder http://localhost:80
2. **Gehe zur PersonalizationPage**
3. **Klicke "LLM Prototyp"** 
4. **Erwarte:**
   - Header zeigt "🧪 Test-Modus - Test-Modus aktiv - Demo-Responses"
   - Segmente werden geladen mit Demo-Feedback
   - Chat funktioniert mit Mock-Responses

## ⚙️ Test-Modus Konfiguration

Der Test-Modus wird automatisch aktiviert wenn:
- Kein `OPENAI_API_KEY` gesetzt ist
- Oder `OPENAI_API_KEY=your_openai_api_key_here` (Beispiel-Key)
- Oder `LLM_TEST_MODE=force` in .env

### Manuell steuern (.env):
```bash
# Auto-Modus (empfohlen)
LLM_TEST_MODE=auto

# Test-Modus erzwingen (auch mit echten Keys)  
LLM_TEST_MODE=force

# Test-Modus deaktivieren (Fehler ohne Keys)
LLM_TEST_MODE=disabled
```

## 🔄 Auf echte API Keys umstellen

Wenn du später echte API Keys verwenden möchtest:

1. **OpenAI Setup:**
   ```bash
   # In .env ersetzen:
   OPENAI_API_KEY=sk-proj-dein-echter-key-hier
   ```

2. **Container neu starten:**
   ```powershell
   docker-compose restart backend
   ```

3. **Status prüfen:**
   ```powershell
   Invoke-WebRequest -UseBasicParsing http://localhost:5000/api/llm/status
   ```
   Erwarte: `"status": "ready", "testMode": false`

## 🎓 Demo-Response Beispiele

Der Test-Modus generiert realistische Antworten:

**Segment 1 (Good):**
> 🧪 [TEST-MODUS] Fantastisch! In diesem Segment zeigst du schon eine sehr gute Kontrolle über Rhythmus und Dynamik. Deine Phrasierung ist ausdrucksvoll und musikalisch durchdacht.

**Segment 2 (Neutral):**  
> 🧪 [TEST-MODUS] Hier sehe ich sowohl Stärken als auch Verbesserungspotential. Die Grundtechnik stimmt, aber wir könnten noch an der Präzision arbeiten. Was denkst du selbst über diesen Abschnitt?

**Segment 3 (Critical):**
> 🧪 [TEST-MODUS] Das ist ein wichtiger Lernbereich! Hier können wir gemeinsam viel erreichen. Lass uns gezielt an der Intonation und dem Timing arbeiten. Hast du Fragen zu diesem Teil?

## ✨ Bereit zum Testen!

Das System ist jetzt perfekt konfiguriert für Entwicklung und Demos ohne API-Kosten. Alle LLM Features sind verfügbar und funktionieren mit realistischen Mock-Responses! 🎵🤖
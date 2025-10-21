# Mudiko - Audio-Feedback-System für Musikschüler

Das Tool ist eine Flask-Webanwendung, die es Musikschülern ermöglicht, ihre Aufnahmen mit Referenzaufnahmen von Lehrkräften zu vergleichen und automatisiertes Feedback zu erhalten. Das System analysiert verschiedene Audio-Features und generiert strukturierte Feedback-Prompts.

## 🎵 Funktionsweise

Das System funktioniert in folgenden Schritten:

1. **Upload**: Schüler laden zwei Audio-Dateien hoch:
   - **Referenz-Aufnahme**: Von der Lehrkraft als Vergleichsstandard
   - **Schüler-Aufnahme**: Die eigene Interpretation des Stücks

2. **Segmentierung**: Beide Aufnahmen werden in 8-Sekunden-Abschnitte unterteilt für detaillierte Analyse

3. **Audio-Analyse**: Für jedes Segment werden umfassende Audio-Features analysiert:
   - **Tempo und Rhythmus**: Geschwindigkeit und rhythmische Stabilität
   - **Tonhöhe**: Melodieverlauf und Intonation
   - **Dynamik**: Lautstärke-Variationen und Ausdruckskraft
   - **Klangfarbe**: Spektrale Eigenschaften und Timbre
   - **Artikulation**: Anschlag und Phrasierung
   - **Harmonie**: Akkorde und Tonarten

4. **Vergleichsanalyse**: Das System vergleicht die Aufnahmen mittels:
   - MFCC-Distanz (Klangfarben-Ähnlichkeit)
   - Chroma-Ähnlichkeit (harmonische Übereinstimmung)
   - DTW-Distanz (zeitliche Ausrichtung)
   - Energie- und Tonhöhen-Korrelationen

5. **Feedback-Generierung**: Basierend auf den Analyse-Ergebnissen wird ein strukturierter Feedback-Prompt erstellt


## 🐳 Docker-Deployment (Installation)

Für die Bereitstellung mit Docker:

Ins APP-Verzeichnis, wo die Docker-Dateien liegen, wechseln 

```bash
cd Verzeichnis/mudiko
```

Docker Starten

Docker-Container starten

```bash
# Image erstellen
docker build -t mudiko .

# Container starten
docker run -p 5000:5000 mudiko
```


## 📁 Projektstruktur

```
mudiko/
├── app/
│   ├── main.py                    # Flask-Hauptanwendung
│   ├── AudioManager.py            # Datei-Management und Segmentierung
│   ├── AudioFeedbackPipeline.py   # Audio-Analyse und Feedback-Generierung
│   ├── templates/                 # HTML-Templates
│   └── Uploads/                   # Upload-Ordner für Audio-Dateien
├── requirements.txt               # Python-Abhängigkeiten
├── Dockerfile                     # Docker-Konfiguration
└── README.md                      # Diese Dokumentation
```

## 🎯 Verwendung

### Web-Interface

1. **Öffnen Sie** `http://localhost:5000` in Ihrem Browser

2. **Laden Sie Dateien hoch**:
   - Wählen Sie eine Referenz-Aufnahme (Lehrkraft)
   - Wählen Sie eine Schüler-Aufnahme
   - Klicken Sie auf "Dateien hochladen"

3. **Konfigurieren Sie die Analyse**:
   - Wählen Sie die Feedback-Sprache
   - Geben Sie die verwendeten Instrumente an
   - Wählen Sie Feedback-Schwerpunkte (optional)

4. **Generieren Sie Feedback**:
   - Klicken Sie auf "Feedback generieren"
   - Das System analysiert beide Aufnahmen
   - Ein strukturierter Feedback-Prompt wird angezeigt

### Unterstützte Audio-Formate

- MP3
- WAV


## 🛠️ Entwicklung

### Code-Struktur

- **`main.py`**: Flask-Routen und Web-Interface
- **`AudioManager`**: Datei-Upload, -speicherung und Segmentierung
- **`AudioFeedbackPipeline`**: Kern-Analyse-Engine


## 📋 Abhängigkeiten

- **Flask**: Web-Framework
- **librosa**: Audio-Analyse-Bibliothek
- **numpy**: Numerische Berechnungen
- **soundfile**: Audio-Datei Ein-/Ausgabe
- **scipy**: Wissenschaftliche Berechnungen
- **sklearn**: Machine Learning (für Ähnlichkeitsmetriken)

## 🚨 Bekannte Einschränkungen

- **Dateigröße**: Große Audio-Dateien (>10MB) können die Verarbeitung verlangsamen
- **Synchronisation**: Der Prompt erkennt nicht zeitliche Versätze zwischen Aufnahmen oder Wiederholungen nach Fehlern.
- **Instrument**: Verschiedene Instrumente erzeugen automatisch unterschiedliche Daten (z.B. Tempo)
- 



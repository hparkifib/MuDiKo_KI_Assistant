# Report Generator Dokumentation

## Übersicht

Das Report-System wurde refactored, um **Separation of Concerns** zu gewährleisten und **Forschungs-Experimente** zu erleichtern.

### Architektur

```
prompt_builder/
├── prompt_generator.py              # System-Prompt (LLM-Aufgabe)
├── base_report_generator.py         # Abstract Base Class
├── report_config.py                 # Konfiguration & Feature-Toggles
├── detailed_report_generator.py     # Detaillierter, pädagogischer Report
├── technical_report_generator.py    # Technischer Feature-Extraction Report
├── selective_report_generator.py    # Report mit Feature-Subset
└── feedback_formatter.py            # (Legacy)
```

---

## 1. PromptGenerator

**Verantwortlichkeit:** Erstellt nur noch den System-Prompt (LLM-Aufgabenstellung).

### Verwendung

```python
from .prompt_builder.prompt_generator import PromptGenerator
from .prompt_builder.report_config import ReportConfig

# Standard (Detailed Report)
prompt_gen = PromptGenerator()

# Mit spezifischer Variante
prompt_gen = PromptGenerator(report_variant='technical')

# Mit Custom Config
config = ReportConfig(
    enabled_features=['tempo', 'mean_pitch'],
    format_style='plain'
)
prompt_gen = PromptGenerator(
    report_variant='selective',
    report_config=config
)

# Feedback generieren
result = prompt_gen.generate_feedback_prompt(
    segment_results=segments,
    language='Deutsch',
    referenz_instrument='Klavier',
    schueler_instrument='Gitarre'
)

print(result['system_prompt'])      # LLM-Aufgabe
print(result['analysis_data'])       # Musik-Report
print(result['report_variant'])      # Verwendete Variante
```

---

## 2. Report-Varianten

### 2.1 Detailed Report (Standard)

**Zweck:** Pädagogisch optimierter Report mit maximalem Kontext.

**Features:**
- ✅ Box-Formatierung (┌─, │, ═)
- ✅ Pädagogische Feature-Namen
- ✅ Referenz/Schüler-Werte nebeneinander
- ✅ Interpretationen ("Sehr ähnlich ✓")
- ✅ Kategorisierung nach musikalischen Aspekten

**Verwendung:**
```python
config = ReportConfig.detailed_report()
gen = PromptGenerator('detailed', config)
```

**Output-Beispiel:**
```
======================================================================
MUSIK-ANALYSE-REPORT (DETAILLIERT)
======================================================================

──────────────────────────────────────────────────────────────────────
Segment 1  |  Zeit: 0.0s - 5.3s
──────────────────────────────────────────────────────────────────────

┌─ TEMPO & RHYTHMUS
│  Tempo (BPM):
│      Referenz:    120.50
│      Schüler:     118.30
│
│  Anzahl Noten:
│      Referenz:    45
│      Schüler:     42
│

┌─ VERGLEICH REFERENZ ↔ SCHÜLER
│  Zeitliche Synchronität:
│      Wert:        4.23
│      Bewertung:   Sehr ähnlich ✓
│
```

---

### 2.2 Technical Report

**Zweck:** Rohe Feature-Daten ohne pädagogische Interpretation.

**Features:**
- ✅ Plain-Text Formatierung
- ✅ Technische Feature-Namen
- ✅ Keine Interpretationen
- ✅ Gruppierung nach Analyse-Typ (temporal, spectral, harmonic, etc.)

**Verwendung:**
```python
config = ReportConfig.technical_report()
gen = PromptGenerator('technical', config)
```

**Output-Beispiel:**
```
======================================================================
FEATURE EXTRACTION REPORT
======================================================================

SEGMENT 1
Time Range: 0.00s - 5.30s
----------------------------------------

TEMPORAL:
  onset_count: 45
  referenz_tempo: 120.50
  rhythm_mean_interval: 0.12
  rhythm_std_interval: 0.03
  schueler_tempo: 118.30

SPECTRAL:
  mean_centroid: 1523.45
  timbre_variance: 234.12

HARMONIC:
  referenz_mean_pitch: 261.63
  schueler_mean_pitch: 259.20

COMPARISON:
  dtw_distance: 4.23
  mfcc_distance: 12.45
  pitch_contour_correlation: 0.87
```

---

### 2.3 Selective Report

**Zweck:** Report mit ausgewählten Features für A/B-Testing.

**Features:**
- ✅ Feature-Toggles via Config
- ✅ Gleiche Formatierung wie Detailed Report
- ✅ Zeigt aktive Features an
- ✅ Ideal für Ablation Studies

**Verwendung:**
```python
# Nur Tempo und Pitch
config = ReportConfig(
    enabled_features=['tempo', 'mean_pitch', 'onset_count'],
    format_style='box',
    include_interpretations=True
)
gen = PromptGenerator('selective', config)

# Mit vordefinierten Feature-Sets
from .report_config import FEATURE_SETS

config = ReportConfig(
    enabled_features=FEATURE_SETS['tempo_only'],
    format_style='box'
)
```

**Output-Beispiel:**
```
======================================================================
MUSIK-ANALYSE-REPORT (SELEKTIV) (3 Features)
======================================================================

Aktive Features:
  tempo, mean_pitch, onset_count

──────────────────────────────────────────────────────────────────────
Segment 1  |  Zeit: 0.0s - 5.3s
──────────────────────────────────────────────────────────────────────

┌─ TEMPO & RHYTHMUS
│  Tempo (BPM):
│      Referenz:    120.50
│      Schüler:     118.30
│
│  Anzahl Noten:
│      Referenz:    45
│      Schüler:     42
│

Hinweis: Dieser Report enthält nur ausgewählte Features.
```

---

## 3. ReportConfig

**Zweck:** Granulare Kontrolle über Report-Verhalten.

### Attribute

| Attribut | Typ | Default | Beschreibung |
|----------|-----|---------|--------------|
| `enabled_features` | `List[str] \| None` | `None` | Aktivierte Features (None = alle) |
| `format_style` | `str` | `'box'` | Formatierung ('box', 'plain', 'markdown') |
| `include_context` | `bool` | `True` | Pädagogische Kontexte |
| `include_interpretations` | `bool` | `True` | Bewertungen ("Sehr ähnlich ✓") |
| `include_comparisons` | `bool` | `True` | Vergleichsmetriken |
| `verbosity_level` | `str` | `'normal'` | Detail-Level ('minimal', 'normal', 'detailed') |
| `show_reference_values` | `bool` | `True` | Referenz-Werte anzeigen |
| `show_student_values` | `bool` | `True` | Schüler-Werte anzeigen |
| `category_order` | `List[str]` | `[...]` | Reihenfolge der Kategorien |

### Factory-Methoden

```python
# Detailed Report (Standard)
config = ReportConfig.detailed_report()

# Technical Report
config = ReportConfig.technical_report()

# Minimal Report
config = ReportConfig.minimal_report(['tempo', 'mean_pitch'])

# Experimental
config = ReportConfig.experimental(
    enabled_features=['tempo', 'mean_rms'],
    format_style='plain',
    include_interpretations=False
)
```

### Vordefinierte Feature-Sets

```python
from .report_config import FEATURE_SETS

FEATURE_SETS = {
    'tempo_only': ['tempo', 'onset_count', 'rhythm_std_interval', 'rhythm_mean_interval'],
    'pitch_only': ['mean_pitch', 'estimated_key', 'dominant_chord', 'vibrato_strength'],
    'dynamics_only': ['mean_rms', 'dynamic_range_db', 'num_silences', 'mean_attack_time'],
    'timbre_only': ['mean_centroid', 'timbre_variance'],
    'comparison_only': ['mfcc_distance', 'chroma_similarity', 'dtw_distance', ...],
    'minimal_core': ['tempo', 'mean_pitch', 'mean_rms'],
    'rhythm_focus': ['tempo', 'onset_count', 'rhythm_std_interval', 'dtw_distance'],
    'pitch_focus': ['mean_pitch', 'estimated_key', 'vibrato_strength', 'pitch_contour_correlation']
}

# Verwendung
config = ReportConfig(enabled_features=FEATURE_SETS['rhythm_focus'])
```

---

## 4. Eigene Report-Variante erstellen

### Schritt 1: BaseReportGenerator erweitern

```python
from .base_report_generator import BaseReportGenerator
from typing import Dict, Any, List

class MyCustomReportGenerator(BaseReportGenerator):
    """Meine eigene Report-Variante."""
    
    def _initialize_feature_mappings(self):
        """Feature-Namen definieren."""
        self.feature_contexts = {
            'tempo': 'Mein Custom Name für Tempo',
            # ...
        }
    
    def generate_report(self, segment_results: List[Dict[str, Any]]) -> str:
        """Report-Generierung implementieren."""
        lines = []
        
        for segment in segment_results:
            analysis = segment.get('analysis', {})
            
            # Feature-Filter nutzen
            for key, value in analysis.items():
                if self._is_feature_enabled(key):
                    # Feature verarbeiten
                    formatted = self._format_value(value)
                    lines.append(f"{key}: {formatted}")
        
        return "\n".join(lines)
```

### Schritt 2: In PromptGenerator registrieren

```python
# In prompt_generator.py
from .my_custom_report import MyCustomReportGenerator

def _create_report_generator(self):
    generators = {
        'detailed': DetailedReportGenerator,
        'technical': TechnicalReportGenerator,
        'selective': SelectiveReportGenerator,
        'custom': MyCustomReportGenerator  # Neu
    }
    # ...
```

### Schritt 3: Verwenden

```python
gen = PromptGenerator(report_variant='custom')
```

---

## 5. Forschungs-Workflows

### A/B-Testing: Feature-Relevanz

```python
# Experiment: Ist Vibrato wichtig?
configs = {
    'with_vibrato': ReportConfig(enabled_features=['tempo', 'mean_pitch', 'vibrato_strength']),
    'without_vibrato': ReportConfig(enabled_features=['tempo', 'mean_pitch'])
}

for name, config in configs.items():
    gen = PromptGenerator('selective', config)
    result = gen.generate_feedback_prompt(...)
    # LLM-Output analysieren und vergleichen
```

### Ablation Study: Kategorien

```python
# Test jede Kategorie einzeln
categories = {
    'tempo_only': FEATURE_SETS['tempo_only'],
    'pitch_only': FEATURE_SETS['pitch_only'],
    'dynamics_only': FEATURE_SETS['dynamics_only'],
    'timbre_only': FEATURE_SETS['timbre_only']
}

results = {}
for name, features in categories.items():
    config = ReportConfig(enabled_features=features)
    gen = PromptGenerator('selective', config)
    results[name] = gen.generate_feedback_prompt(...)
```

### Token-Optimierung

```python
# Finde minimales Feature-Set für gute Ergebnisse
minimal_configs = [
    ReportConfig(enabled_features=['tempo']),
    ReportConfig(enabled_features=['tempo', 'mean_pitch']),
    ReportConfig(enabled_features=['tempo', 'mean_pitch', 'mean_rms']),
    # ...
]

for config in minimal_configs:
    gen = PromptGenerator('selective', config)
    result = gen.generate_feedback_prompt(...)
    token_count = count_tokens(result['analysis_data'])
    print(f"Features: {len(config.enabled_features)}, Tokens: {token_count}")
```

---

## 6. Best Practices

### ✅ Do's

1. **Verwende Factory-Methoden** für Standard-Configs:
   ```python
   config = ReportConfig.detailed_report()
   ```

2. **Nutze vordefinierte Feature-Sets**:
   ```python
   config = ReportConfig(enabled_features=FEATURE_SETS['rhythm_focus'])
   ```

3. **Dokumentiere Experimente**:
   ```python
   # Experiment 2025-12-09: Vibrato-Relevanz
   config = ReportConfig(
       enabled_features=['tempo', 'vibrato_strength'],
       include_interpretations=True
   )
   ```

4. **Teste mit kleinen Feature-Sets** zuerst

### ❌ Don'ts

1. **Nicht direkt Report-Generatoren instanziieren** (nutze PromptGenerator)
2. **Nicht Feature-Namen hardcoden** (nutze FEATURE_SETS)
3. **Nicht Config-Dict manuell bauen** (nutze ReportConfig)

---

## 7. Migration von Alt zu Neu

### Vorher (Monolithisch)

```python
prompt_gen = PromptGenerator()
result = prompt_gen.generate_feedback_prompt(segments, ...)
```

### Nachher (Modular)

```python
# Standard (identisch)
prompt_gen = PromptGenerator()
result = prompt_gen.generate_feedback_prompt(segments, ...)

# Mit Varianten
prompt_gen = PromptGenerator(report_variant='technical')
result = prompt_gen.generate_feedback_prompt(segments, ...)

# Mit Custom Config
config = ReportConfig(enabled_features=['tempo', 'mean_pitch'])
prompt_gen = PromptGenerator('selective', config)
result = prompt_gen.generate_feedback_prompt(segments, ...)
```

**Kompatibilität:** Alte Nutzung funktioniert weiterhin (Detailed Report = Standard).

---

## 8. Verfügbare Features

| Feature-Name | Kategorie | Beschreibung |
|--------------|-----------|--------------|
| `tempo` | Tempo & Rhythmus | Tempo in BPM |
| `onset_count` | Tempo & Rhythmus | Anzahl Noten |
| `rhythm_std_interval` | Tempo & Rhythmus | Rhythmus-Gleichmäßigkeit |
| `rhythm_mean_interval` | Tempo & Rhythmus | Durchschn. Notenabstand |
| `mean_pitch` | Tonhöhe & Harmonie | Durchschn. Tonhöhe |
| `estimated_key` | Tonhöhe & Harmonie | Tonart |
| `dominant_chord` | Tonhöhe & Harmonie | Hauptakkord |
| `vibrato_strength` | Tonhöhe & Harmonie | Vibrato-Intensität |
| `mean_rms` | Lautstärke & Dynamik | Durchschn. Lautstärke |
| `dynamic_range_db` | Lautstärke & Dynamik | Dynamikumfang |
| `num_silences` | Lautstärke & Dynamik | Anzahl Pausen |
| `mean_attack_time` | Lautstärke & Dynamik | Anschlagsgeschwindigkeit |
| `mean_centroid` | Klangfarbe | Klangfarbe |
| `timbre_variance` | Klangfarbe | Klangfarben-Konsistenz |
| `mfcc_distance` | Vergleich | Klangfarben-Ähnlichkeit |
| `chroma_similarity` | Vergleich | Harmonische Ähnlichkeit |
| `dtw_distance` | Vergleich | Zeitliche Synchronität |
| `rms_correlation` | Vergleich | Dynamik-Ähnlichkeit |
| `pitch_contour_correlation` | Vergleich | Melodie-Ähnlichkeit |

---

## Support & Erweiterungen

**Neue Report-Variante gewünscht?** Erweitere `BaseReportGenerator` und registriere in `PromptGenerator`.

**Neue Features hinzufügen?** Ergänze in `feature_contexts` Dict der jeweiligen Report-Klasse.

**Fragen?** Siehe Code-Kommentare oder öffne ein Issue.

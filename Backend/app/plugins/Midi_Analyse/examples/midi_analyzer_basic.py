"""
Beispiel: Basis-Verwendung des MIDI Analyzer

Zeigt die grundlegende Verwendung für lokale Scripts.
"""

from midi_analyzer import MidiAnalyzer

# Erstelle Analyzer-Instanz
analyzer = MidiAnalyzer()


# ===== Beispiel 1: Einzelne Datei analysieren =====
def beispiel_einzelanalyse():
    print("Beispiel 1: Einzelne Datei analysieren")
    print("=" * 50)
    
    result = analyzer.analyze_file("test_data/Amazing_Grace.mid")
    
    print(f"Datei: {result.filename}")
    print(f"Länge: {result.length_seconds:.2f} Sekunden")
    print(f"Tracks: {result.total_tracks}")
    print(f"Noten: {result.total_notes}")
    
    # Als JSON
    json_output = result.to_json()
    print(f"\nJSON-Länge: {len(json_output)} Zeichen")
    
    # Als Dict
    data = result.to_dict()
    print(f"Erster Track: {data['tracks'][0]['track_name']}")
    
    print()


# ===== Beispiel 2: Zwei Dateien vergleichen =====
def beispiel_vergleich():
    print("Beispiel 2: Zwei Dateien vergleichen")
    print("=" * 50)
    
    result = analyzer.compare_files(
        "test_data/Amazing_Grace Referenz linke Hand.mid",
        "test_data/Amazing_Grace falsche Töne linke Hand.mid"
    )
    
    print(f"Referenz: {result.file1_analysis.filename}")
    print(f"Vergleich: {result.file2_analysis.filename}")
    
    if result.summary:
        print(f"\nUnterschie: {result.summary.total_differences}")
        print(f"Ähnlichkeit: {result.summary.similarity_score * 100:.1f}%")
    
    # Zeige erste 3 Unterschiede
    differences = result.get_differences()
    print(f"\nErste 3 Unterschiede:")
    for i, diff in enumerate(differences[:3], 1):
        print(f"  {i}. {diff['message']}")
    
    print()


# ===== Beispiel 3: Bytes analysieren (für Uploads) =====
def beispiel_bytes():
    print("Beispiel 3: Bytes analysieren")
    print("=" * 50)
    
    # Lese Datei als Bytes
    with open("test_data/Amazing_Grace.mid", "rb") as f:
        data = f.read()
    
    result = analyzer.analyze_bytes(data, "amazing_grace.mid")
    
    print(f"Bytes analysiert: {len(data)} Bytes")
    print(f"Gefunden: {result.total_notes} Noten")
    
    print()


# ===== Beispiel 4: Text-Output speichern =====
def beispiel_text_output():
    print("Beispiel 4: Text-Output speichern")
    print("=" * 50)
    
    from midi_analyzer import TextFormatter
    
    result = analyzer.compare_files(
        "test_data/Amazing_Grace Referenz linke Hand.mid",
        "test_data/Amazing_Grace falsche Töne linke Hand.mid"
    )
    
    formatter = TextFormatter()
    text_output = formatter.format_comparison(result)
    
    # Speichere
    with open("output_example.txt", "w", encoding="utf-8") as f:
        f.write(text_output)
    
    print("Text-Vergleich gespeichert in: output_example.txt")
    print(f"Länge: {len(text_output)} Zeichen")
    
    print()


if __name__ == "__main__":
    # Führe alle Beispiele aus
    try:
        beispiel_einzelanalyse()
        beispiel_vergleich()
        beispiel_bytes()
        beispiel_text_output()
        
        print("✓ Alle Beispiele erfolgreich ausgeführt!")
    
    except FileNotFoundError as e:
        print(f"Fehler: Datei nicht gefunden - {e}")
        print("Stelle sicher, dass die Test-MIDI-Dateien vorhanden sind.")
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

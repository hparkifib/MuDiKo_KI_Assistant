"""
CLI-Anwendung für MIDI-Analyse
Kommandozeilen-Interface für lokale Nutzung
"""

import argparse
import sys
import os

# Füge Parent-Directory zum Path hinzu für lokale Entwicklung
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from midi_analyzer import MidiAnalyzer, TextFormatter


def main():
    """Hauptfunktion für CLI"""
    parser = argparse.ArgumentParser(
        description='MIDI-Analyse und -Vergleich Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Beispiele:
  # Einzelne Datei analysieren
  python cli_app.py analyze song.mid -o analysis.txt
  
  # Zwei Dateien vergleichen
  python cli_app.py compare reference.mid performance.mid -o comparison.txt
  
  # JSON-Output
  python cli_app.py analyze song.mid -o output.json --format json
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Verfügbare Befehle')
    
    # Analyze Command
    analyze_parser = subparsers.add_parser('analyze', help='Analysiert eine MIDI-Datei')
    analyze_parser.add_argument('file', help='MIDI-Datei zum Analysieren')
    analyze_parser.add_argument('-o', '--output', default='analysis.txt',
                               help='Ausgabe-Datei (Standard: analysis.txt)')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Ausgabe-Format (Standard: text)')
    
    # Compare Command
    compare_parser = subparsers.add_parser('compare', help='Vergleicht zwei MIDI-Dateien')
    compare_parser.add_argument('file1', help='Erste MIDI-Datei (Referenz)')
    compare_parser.add_argument('file2', help='Zweite MIDI-Datei (Vergleich)')
    compare_parser.add_argument('-o', '--output', default='comparison.txt',
                               help='Ausgabe-Datei (Standard: comparison.txt)')
    compare_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Ausgabe-Format (Standard: text)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        analyzer = MidiAnalyzer()
        
        if args.command == 'analyze':
            print(f"Analysiere {args.file}...")
            result = analyzer.analyze_file(args.file)
            
            if args.format == 'json':
                output = result.to_json()
            else:
                formatter = TextFormatter()
                output = formatter.format_analysis(result)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            
            print(f"✓ Analyse gespeichert in: {args.output}")
            print(f"  Gefundene Noten: {result.total_notes}")
            print(f"  Tracks: {result.total_tracks}")
        
        elif args.command == 'compare':
            print(f"Vergleiche:")
            print(f"  Referenz:  {args.file1}")
            print(f"  Vergleich: {args.file2}")
            
            result = analyzer.compare_files(args.file1, args.file2)
            
            if args.format == 'json':
                output = result.to_json()
            else:
                formatter = TextFormatter()
                output = formatter.format_comparison(result)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            
            print(f"✓ Vergleich gespeichert in: {args.output}")
            if result.summary:
                print(f"  Unterschiede: {result.summary.total_differences}")
                print(f"  Ähnlichkeit: {result.summary.similarity_score * 100:.1f}%")
    
    except FileNotFoundError as e:
        print(f"✗ Fehler: Datei nicht gefunden - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Fehler: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

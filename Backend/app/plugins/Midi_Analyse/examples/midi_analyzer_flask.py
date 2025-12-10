"""
Beispiel: Flask Backend-Integration

Zeigt, wie man den MIDI Analyzer in eine Flask-Anwendung integriert.
"""

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from midi_analyzer import MidiAnalyzer

app = Flask(__name__)
analyzer = MidiAnalyzer()


@app.route('/api/midi/analyze', methods=['POST'])
def analyze_midi():
    """Analysiert eine hochgeladene MIDI-Datei"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Keine Datei hochgeladen"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Keine Datei ausgewählt"}), 400
        
        # Lese und analysiere
        data = file.read()
        result = analyzer.analyze_bytes(data, file.filename)
        
        return jsonify(result.to_dict())
    
    except ValueError as e:
        return jsonify({"error": f"Ungültige MIDI-Datei: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Serverfehler: {str(e)}"}), 500


@app.route('/api/midi/compare', methods=['POST'])
def compare_midi():
    """Vergleicht zwei MIDI-Dateien"""
    try:
        if 'reference' not in request.files or 'comparison' not in request.files:
            return jsonify({"error": "Beide Dateien müssen hochgeladen werden"}), 400
        
        ref_file = request.files['reference']
        comp_file = request.files['comparison']
        
        # Lese und vergleiche
        ref_data = ref_file.read()
        comp_data = comp_file.read()
        
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            ref_file.filename, comp_file.filename
        )
        
        return jsonify(result.to_dict())
    
    except ValueError as e:
        return jsonify({"error": f"Ungültige MIDI-Datei: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Serverfehler: {str(e)}"}), 500


@app.route('/api/midi/compare/summary', methods=['POST'])
def compare_midi_summary():
    """Vergleicht zwei MIDI-Dateien - nur Zusammenfassung"""
    try:
        ref_file = request.files['reference']
        comp_file = request.files['comparison']
        
        ref_data = ref_file.read()
        comp_data = comp_file.read()
        
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            ref_file.filename, comp_file.filename
        )
        
        return jsonify(result.get_summary())
    
    except ValueError as e:
        return jsonify({"error": f"Ungültige MIDI-Datei: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Serverfehler: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health-Check Endpoint"""
    return jsonify({"status": "healthy", "service": "midi-analyzer"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

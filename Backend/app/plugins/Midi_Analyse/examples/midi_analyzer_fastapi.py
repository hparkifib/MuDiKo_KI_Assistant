"""
Beispiel: FastAPI Backend-Integration

Zeigt, wie man den MIDI Analyzer in eine FastAPI-Anwendung integriert.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from midi_analyzer import MidiAnalyzer

app = FastAPI(title="MIDI Analyzer API")
analyzer = MidiAnalyzer()


@app.post("/api/midi/analyze")
async def analyze_midi(file: UploadFile = File(...)):
    """
    Analysiert eine hochgeladene MIDI-Datei
    
    Returns:
        JSON mit vollständiger Analyse
    """
    try:
        # Lese File-Content
        content = await file.read()
        
        # Analysiere
        result = analyzer.analyze_bytes(content, file.filename)
        
        # Gib Analyse als JSON zurück
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige MIDI-Datei: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")


@app.post("/api/midi/compare")
async def compare_midi(
    reference: UploadFile = File(...),
    comparison: UploadFile = File(...)
):
    """
    Vergleicht zwei MIDI-Dateien
    
    Returns:
        JSON mit Vergleichsergebnis und Unterschieden
    """
    try:
        # Lese beide Files
        ref_data = await reference.read()
        comp_data = await comparison.read()
        
        # Vergleiche
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            reference.filename, comparison.filename
        )
        
        # Gib vollständigen Vergleich zurück
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige MIDI-Datei: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")


@app.post("/api/midi/compare/summary")
async def compare_midi_summary(
    reference: UploadFile = File(...),
    comparison: UploadFile = File(...)
):
    """
    Vergleicht zwei MIDI-Dateien und gibt nur Zusammenfassung zurück
    
    Returns:
        JSON mit kompakter Zusammenfassung
    """
    try:
        ref_data = await reference.read()
        comp_data = await comparison.read()
        
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            reference.filename, comparison.filename
        )
        
        # Nur Zusammenfassung
        return result.get_summary()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige MIDI-Datei: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")


@app.post("/api/midi/compare/differences")
async def compare_midi_differences(
    reference: UploadFile = File(...),
    comparison: UploadFile = File(...)
):
    """
    Vergleicht zwei MIDI-Dateien und gibt nur Unterschiede zurück
    
    Returns:
        JSON mit Liste der Unterschiede
    """
    try:
        ref_data = await reference.read()
        comp_data = await comparison.read()
        
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            reference.filename, comparison.filename
        )
        
        # Nur Unterschiede
        return {"differences": result.get_differences()}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige MIDI-Datei: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serverfehler: {str(e)}")


@app.get("/health")
async def health_check():
    """Health-Check Endpoint"""
    return {"status": "healthy", "service": "midi-analyzer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

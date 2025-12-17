import { useState, useEffect } from 'react';

export default function Mp3ToMidiPresetSelectionPage({ onBack, onNext }) {
  const [selectedPreset, setSelectedPreset] = useState('piano');
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [converting, setConverting] = useState(false);

  // Lade Presets vom Backend
  useEffect(() => {
    const loadPresets = async () => {
      try {
        const response = await fetch('/api/tools/mp3-to-midi-feedback/presets');
        const data = await response.json();
        
        if (data.success && data.presets) {
          setPresets(data.presets);
        } else {
          throw new Error('Keine Presets verfügbar');
        }
      } catch (err) {
        console.error('Error loading presets:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPresets();
  }, []);

  const handleNext = async () => {
    setConverting(true);
    setError(null);

    try {
      const sessionId = localStorage.getItem('mp3ToMidiSessionId');
      if (!sessionId) {
        throw new Error('Keine Session gefunden');
      }

      const response = await fetch('/api/tools/mp3-to-midi-feedback/convert', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({ 
          sessionId,
          presetId: selectedPreset
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        localStorage.setItem('mp3ToMidiConversionData', JSON.stringify(result.result));
        setTimeout(() => onNext(), 500);
      } else {
        throw new Error(result.error || 'Konversion fehlgeschlagen');
      }
    } catch (err) {
      setError(err.message);
      setConverting(false);
    }
  };

  const currentPreset = presets.find(p => p.id === selectedPreset);

  return (
    <div style={{ 
      minHeight: '100vh',
      minHeight: '100dvh',
      height: '100dvh',
      width: '100%', 
      backgroundColor: 'var(--bg-color)', 
      backgroundImage: 'url(/Rainbow-Line.svg)', 
      backgroundPosition: 'top', 
      backgroundRepeat: 'no-repeat', 
      backgroundSize: 'contain', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'space-between', 
      alignItems: 'center' 
    }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Instrument-Preset auswählen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ 
                display: 'inline-block',
                width: '50px',
                height: '50px',
                border: '4px solid var(--button-color)',
                borderTop: '4px solid var(--mudiko-pink)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                marginBottom: '20px'
              }} />
              <p style={{ color: 'var(--font-color)', margin: '0' }}>Lade Presets...</p>
            </div>
          ) : converting ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ 
                display: 'inline-block',
                width: '50px',
                height: '50px',
                border: '4px solid var(--button-color)',
                borderTop: '4px solid var(--mudiko-pink)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                marginBottom: '20px'
              }} />
              <h3 style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>
                🎹 MIDI-Konvertierung läuft...
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                Basic Pitch analysiert die Audio-Dateien mit deinem gewählten Preset.
                Dies kann bis zu 2 Minuten dauern.
              </p>
            </div>
          ) : error ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <p style={{ color: '#ff6b6b', fontSize: '16px' }}>⚠️ {error}</p>
            </div>
          ) : (
            <>
              <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
                Wähle das passende Preset für dein Instrument, um die MIDI-Konvertierung zu optimieren:
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
                {/* Preset-Auswahl */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Instrument</span>
                    <select 
                      value={selectedPreset} 
                      onChange={(e) => setSelectedPreset(e.target.value)}
                      style={{ 
                        backgroundColor: 'var(--button-color)', 
                        color: 'var(--font-color)', 
                        border: 'none', 
                        borderRadius: '5px', 
                        padding: '5px 10px',
                        fontFamily: "'Nunito', sans-serif"
                      }}
                    >
                      {presets.map((preset) => (
                        <option key={preset.id} value={preset.id}>
                          {preset.icon} {preset.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Preset-Details */}
                {currentPreset && (
                  <div style={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.2)', 
                    borderRadius: '10px', 
                    padding: '15px',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                      <span style={{ fontSize: '32px', marginRight: '12px' }}>{currentPreset.icon}</span>
                      <h3 style={{ color: 'var(--font-color)', margin: '0', fontSize: '20px' }}>
                        {currentPreset.name}
                      </h3>
                    </div>
                    
                    <div style={{ marginBottom: '12px' }}>
                      <p style={{ 
                        color: 'var(--mudiko-cyan)', 
                        fontSize: '12px', 
                        fontWeight: '600', 
                        textTransform: 'uppercase', 
                        letterSpacing: '0.5px',
                        margin: '0 0 5px 0'
                      }}>
                        Beschreibung
                      </p>
                      <p style={{ color: 'var(--font-color)', fontSize: '14px', lineHeight: '1.5', margin: '0' }}>
                        {currentPreset.description}
                      </p>
                    </div>

                    <div>
                      <p style={{ 
                        color: 'var(--mudiko-cyan)', 
                        fontSize: '12px', 
                        fontWeight: '600', 
                        textTransform: 'uppercase', 
                        letterSpacing: '0.5px',
                        margin: '0 0 5px 0'
                      }}>
                        Instrumente
                      </p>
                      <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>
                        {(currentPreset.instruments || []).join(', ')}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>

      <div style={{ display: 'flex', justifyContent: 'space-between', width: '95%', marginBottom: '20px' }}>
        <button 
          onClick={onBack}
          disabled={converting}
          style={{
            backgroundColor: 'var(--button-color)',
            color: 'var(--font-color)',
            border: '2px solid #666666',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: converting ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: converting ? 0.5 : 1
          }}
          onMouseEnter={(e) => !converting && (e.target.style.transform = 'scale(1.02)')}
          onMouseLeave={(e) => !converting && (e.target.style.transform = 'scale(1)')}
        >
          ← Zurück
        </button>
        <button 
          onClick={handleNext}
          disabled={loading || converting || error}
          style={{ 
            backgroundColor: 'var(--button-color)',
            border: '2px solid #666666', 
            color: 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: (loading || converting || error) ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: (loading || converting || error) ? 0.5 : 1
          }} 
          onMouseEnter={(e) => !(loading || converting || error) && (e.target.style.transform = 'scale(1.02)')}
          onMouseLeave={(e) => !(loading || converting || error) && (e.target.style.transform = 'scale(1)')}
        >
          Konvertieren →
        </button>
      </div>
    </div>
  );
}

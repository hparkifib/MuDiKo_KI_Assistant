import { useState, useEffect } from 'react';

/**
 * Konvertierungs-Seite - Zeigt Ladeanimation während MIDI-Konvertierung.
 * 
 * Startet automatisch die Konvertierung im Auto-Modus (ohne Preset)
 * und leitet bei Erfolg zur Result-Page weiter.
 */
export default function Mp3ToMidiConvertingPage({ onBack, onNext }) {
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('Analysiere Audio...');

  useEffect(() => {
    const startConversion = async () => {
      try {
        const sessionId = localStorage.getItem('mp3ToMidiSessionId');
        if (!sessionId) {
          throw new Error('Keine Session gefunden. Bitte lade die Dateien erneut hoch.');
        }

        setStatus('Analysiere Audio-Eigenschaften...');
        
        // Kurze Verzögerung für bessere UX
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setStatus('Konvertiere zu MIDI...');

        const response = await fetch('/api/tools/mp3-to-midi-feedback/convert', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-Session-ID': sessionId
          },
          body: JSON.stringify({ 
            sessionId,
            presetId: null  // Auto-Modus: Optimizer berechnet alle Parameter
          })
        });

        const result = await response.json();

        if (response.ok && result.success) {
          setStatus('Konvertierung abgeschlossen!');
          localStorage.setItem('mp3ToMidiConversionData', JSON.stringify(result.result));
          
          // Kurze Verzögerung damit User "abgeschlossen" sieht
          setTimeout(() => onNext(), 800);
        } else {
          throw new Error(result.error || 'Konvertierung fehlgeschlagen');
        }
      } catch (err) {
        console.error('Conversion error:', err);
        setError(err.message);
      }
    };

    startConversion();
  }, [onNext]);

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
        {/* Header */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>MIDI-Konvertierung</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        {/* Content Card */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {error ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <p style={{ color: '#ff6b6b', fontSize: '16px' }}>⚠️ {error}</p>
              <button
                onClick={onBack}
                style={{
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 30px',
                  fontSize: '16px',
                  cursor: 'pointer',
                  fontFamily: "'Nunito', sans-serif",
                  marginTop: '15px'
                }}
              >
                Zurück zum Upload
              </button>
            </div>
          ) : (
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
                🎹 {status}
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                Die Audio-Dateien werden analysiert und zu MIDI konvertiert.
                Dies kann bis zu 2 Minuten dauern.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer spacer */}
      <div style={{ height: '20px' }} />

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

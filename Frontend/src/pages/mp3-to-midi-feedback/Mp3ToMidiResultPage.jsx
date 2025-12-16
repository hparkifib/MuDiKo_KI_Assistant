import { useState, useEffect } from 'react'

export default function Mp3ToMidiResultPage({ onBack, onHome }) {
  const [conversionData, setConversionData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Lade Konversionsdaten aus localStorage
    try {
      const storedData = localStorage.getItem('mp3ToMidiConversionData');
      const sessionId = localStorage.getItem('mp3ToMidiSessionId');
      
      if (!storedData || !sessionId) {
        setError('Keine Konversionsdaten gefunden. Bitte starte den Upload-Prozess erneut.');
      } else {
        const data = JSON.parse(storedData);
        setConversionData({ ...data, sessionId });
      }
    } catch (err) {
      setError('Fehler beim Laden der Konversionsdaten.');
      console.error('Error loading conversion data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDownload = async (role) => {
    if (!conversionData?.sessionId) return;

    // Extract MIDI filename from path
    const midiPath = role === 'referenz' 
      ? conversionData.referenz?.midi_path
      : conversionData.schueler?.midi_path;

    if (!midiPath) {
      alert('MIDI-Datei nicht gefunden.');
      return;
    }

    // Extract just the filename (e.g., "referenz_referenz.mid")
    const filename = midiPath.split('/').pop();

    try {
      // The backend will automatically check the midi/ subdirectory
      const response = await fetch(`/api/audio/${filename}?sessionId=${encodeURIComponent(conversionData.sessionId)}`);
      
      if (!response.ok) {
        throw new Error('Download fehlgeschlagen');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Fehler beim Herunterladen der MIDI-Datei.');
    }
  };

  const handleNewConversion = () => {
    // Cleanup
    localStorage.removeItem('mp3ToMidiConversionData');
    if (onBack) {
      onBack();
    }
  };

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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>MIDI-Konvertierung Abgeschlossen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
              <div style={{ 
                color: 'var(--font-color)', 
                fontSize: '16px',
                animation: 'pulse 1.5s infinite'
              }}>
                🎵 Lade Ergebnisse...
              </div>
            </div>
          ) : error ? (
            <div style={{ 
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              borderRadius: '15px', 
              padding: '20px',
              border: '2px solid #ff6b6b',
              textAlign: 'center'
            }}>
              <p style={{ color: '#ff6b6b', margin: '0', fontWeight: '600' }}>
                ⚠️ {error}
              </p>
            </div>
          ) : conversionData ? (
            <>
              {/* Download Cards */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {/* Referenz MIDI */}
                <div style={{ 
                  backgroundColor: 'rgba(135, 189, 207, 0.1)',
                  borderRadius: '15px',
                  padding: '20px',
                  border: '2px solid var(--mudiko-cyan)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h3 style={{ color: 'var(--font-color)', margin: '0 0 5px 0', fontSize: '18px', fontWeight: '600' }}>
                      🎼 Referenz-MIDI
                    </h3>
                    <p style={{ color: 'var(--font-color)', margin: '0', fontSize: '14px', opacity: 0.7 }}>
                      {conversionData.referenz?.midi_path?.split('/').pop() || 'Nicht verfügbar'}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDownload('referenz')}
                    style={{
                      background: 'var(--button-color)',
                      border: '2px solid',
                      borderImage: 'var(--mudiko-gradient) 1',
                      color: 'var(--font-color)',
                      padding: '10px 20px',
                      borderRadius: '10px',
                      cursor: 'pointer',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: '16px',
                      fontWeight: '600',
                      boxShadow: 'var(--shadow)',
                      transition: 'transform 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                  >
                    ⬇️ Download
                  </button>
                </div>

                {/* Schüler MIDI */}
                <div style={{ 
                  backgroundColor: 'rgba(255, 158, 161, 0.1)',
                  borderRadius: '15px',
                  padding: '20px',
                  border: '2px solid var(--mudiko-pink)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h3 style={{ color: 'var(--font-color)', margin: '0 0 5px 0', fontSize: '18px', fontWeight: '600' }}>
                      🎹 Deine MIDI-Datei
                    </h3>
                    <p style={{ color: 'var(--font-color)', margin: '0', fontSize: '14px', opacity: 0.7 }}>
                      {conversionData.schueler?.midi_path?.split('/').pop() || 'Nicht verfügbar'}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDownload('schueler')}
                    style={{
                      background: 'var(--button-color)',
                      border: '2px solid',
                      borderImage: 'var(--mudiko-gradient) 1',
                      color: 'var(--font-color)',
                      padding: '10px 20px',
                      borderRadius: '10px',
                      cursor: 'pointer',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: '16px',
                      fontWeight: '600',
                      boxShadow: 'var(--shadow)',
                      transition: 'transform 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                  >
                    ⬇️ Download
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0' }}>
                Keine Daten verfügbar.
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Spacing */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '90%', marginBottom: '20px' }}>
        <button
          onClick={() => { if (onHome) onHome(); }}
          style={{
            backgroundColor: 'var(--button-color)',
            color: 'var(--font-color)',
            border: '2px solid #666666',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          🏠 Zurück zur Startseite
        </button>
        <button
          onClick={handleNewConversion}
          style={{
            background: 'var(--button-color)',
            border: '2px solid',
            borderImage: 'var(--mudiko-gradient) 1',
            color: 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          🔄 Neue Konvertierung
        </button>
      </div>
    </div>
  )
}

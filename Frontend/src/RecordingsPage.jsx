import { useState, useEffect } from 'react'

export default function RecordingsPage({ onBack, onNext }) {
  const [uploadData, setUploadData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load upload data from localStorage
    try {
      const storedData = localStorage.getItem('uploadData');
      if (storedData) {
        const data = JSON.parse(storedData);
        setUploadData(data);
      } else {
        setError('Keine Upload-Daten gefunden. Bitte laden Sie zuerst Ihre Audiodateien hoch.');
      }
    } catch (err) {
      setError('Fehler beim Laden der Upload-Daten.');
      console.error('Error loading upload data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getAudioUrl = (filename) => {
    const sessionId = uploadData?.sessionId || localStorage.getItem('sessionId');
    if (!sessionId) return null;
    return `/api/audio/${filename}?sessionId=${encodeURIComponent(sessionId)}`;
  };
  return (
    <div style={{ 
      minHeight: '100vh', /* Fallback für ältere Browser */
      minHeight: '100dvh', /* Dynamic Viewport Height - berücksichtigt Toolbar */
      height: '100dvh', /* Feste Höhe für optimale Platznutzung */
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Deine Aufnahmen</h1>
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
                🎵 Lade Aufnahmen...
              </div>
            </div>
          ) : error ? (
            <div style={{ 
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              borderRadius: '0px', 
              padding: '20px',
              border: '2px solid #ff6b6b',
              textAlign: 'center'
            }}>
              <p style={{ color: '#ff6b6b', margin: '0', fontWeight: '600' }}>
                ⚠️ {error}
              </p>
            </div>
          ) : uploadData ? (
            <>            
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Reference Audio */}
                <div style={{ 
                  backgroundColor: 'rgba(135, 189, 207, 0.1)',
                  borderRadius: '15px',
                  padding: '15px',
                  border: '2px solid var(--mudiko-cyan)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--mudiko-cyan)',
                        marginRight: '10px'
                      }} />
                      <h3 style={{ color: 'var(--font-color)', margin: '0', fontSize: '18px', fontWeight: '600' }}>
                        Referenz-Aufnahme
                      </h3>
                    </div>
                    <p style={{ color: 'var(--font-color)', margin: '0', fontSize: '14px', opacity: 0.8 }}>
                      🎵 {uploadData.original_filenames?.referenz || 'Unbekannte Datei'}
                    </p>
                  </div>
                  
                  {uploadData.file_map?.referenz ? (
                    <audio 
                      controls 
                      style={{ 
                        width: '100%',
                        height: '40px',
                        backgroundColor: 'var(--button-color)',
                        borderRadius: '8px',
                        outline: 'none'
                      }}
                      preload="metadata"
                    >
                      <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/mpeg" />
                      <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/wav" />
                      <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/mp4" />
                      Dein Browser unterstützt das Audio-Element nicht.
                    </audio>
                  ) : (
                    <div style={{ color: '#ff6b6b', fontSize: '14px' }}>
                      ⚠️ Referenz-Datei nicht gefunden
                    </div>
                  )}
                </div>

                {/* Student Audio */}
                <div style={{ 
                  backgroundColor: 'rgba(255, 158, 161, 0.1)',
                  borderRadius: '15px',
                  padding: '15px',
                  border: '2px solid var(--mudiko-pink)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--mudiko-pink)',
                        marginRight: '10px'
                      }} />
                      <h3 style={{ color: 'var(--font-color)', margin: '0', fontSize: '18px', fontWeight: '600' }}>
                        Deine Aufnahme
                      </h3>
                    </div>
                    <p style={{ color: 'var(--font-color)', margin: '0', fontSize: '14px', opacity: 0.8 }}>
                      🎵 {uploadData.original_filenames?.schueler || 'Unbekannte Datei'}
                    </p>
                  </div>
                  
                  {uploadData.file_map?.schueler ? (
                    <audio 
                      controls 
                      style={{ 
                        width: '100%',
                        height: '40px',
                        backgroundColor: 'var(--button-color)',
                        borderRadius: '8px',
                        outline: 'none'
                      }}
                      preload="metadata"
                    >
                      <source src={getAudioUrl(uploadData.file_map.schueler)} type="audio/mpeg" />
                      <source src={getAudioUrl(uploadData.file_map.schueler)} type="audio/wav" />
                      <source src={getAudioUrl(uploadData.file_map.schueler)} type="audio/mp4" />
                      Dein Browser unterstützt das Audio-Element nicht.
                    </audio>
                  ) : (
                    <div style={{ color: '#ff6b6b', fontSize: '14px' }}>
                      ⚠️ Schüler-Datei nicht gefunden
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0' }}>
                Keine Aufnahmen verfügbar. Bitte laden Sie zuerst Ihre Audiodateien hoch.
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '95%', marginBottom: '20px' }}>
        <button 
          onClick={onBack}
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
          ← Zurück
        </button>
        
        <button 
          style={{ 
            backgroundColor: 'var(--button-color)',
            border: '2px solid #666666', 
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
          onClick={onNext}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          Weiter →
        </button>
      </div>
    </div>
  )
}

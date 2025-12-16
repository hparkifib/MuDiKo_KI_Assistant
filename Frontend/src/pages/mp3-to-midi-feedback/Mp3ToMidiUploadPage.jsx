// MP3-to-MIDI Upload Page - Phase 1
import { useState } from 'react'

export default function Mp3ToMidiUploadPage({ onNext, onShowResult }) {
  const [refFile, setRefFile] = useState(null);
  const [studentFile, setStudentFile] = useState(null);
  const [refFileName, setRefFileName] = useState('');
  const [studentFileName, setStudentFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [conversionStatus, setConversionStatus] = useState(null);

  const handleUpload = async () => {
    if (!refFile || !studentFile) {
      setUploadStatus({ type: 'error', message: 'Bitte wähle beide Audiodateien aus' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      // Cleanup alte Session
      let sessionId = localStorage.getItem('mp3ToMidiSessionId');
      if (sessionId) {
        try {
          await fetch('/api/tools/mp3-to-midi-feedback/session/cleanup', {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'X-Session-ID': sessionId
            },
            body: JSON.stringify({ sessionId })
          });
        } catch {}
        localStorage.removeItem('mp3ToMidiSessionId');
        sessionId = null;
      }

      // Upload
      const formData = new FormData();
      formData.append('referenz', refFile);
      formData.append('schueler', studentFile);

      const response = await fetch('/api/tools/mp3-to-midi-feedback/upload', {
        method: 'POST',
        body: formData,
        headers: sessionId ? { 'X-Session-ID': sessionId } : {},
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus({ type: 'success', message: 'Dateien erfolgreich hochgeladen!' });
        
        if (result.sessionId) {
          localStorage.setItem('mp3ToMidiSessionId', result.sessionId);
          
          // Starte automatisch die Konversion
          setTimeout(() => {
            handleConversion(result.sessionId);
          }, 1000);
        }
      } else {
        setUploadStatus({ type: 'error', message: result.error || 'Fehler beim Hochladen' });
      }
    } catch (error) {
      setUploadStatus({ type: 'error', message: 'Verbindungsfehler zum Server' });
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleConversion = async (sessionId) => {
    setIsConverting(true);
    setConversionStatus({ type: 'info', message: 'Konvertiere MP3 zu MIDI via Basic Pitch...' });

    try {
      const response = await fetch('/api/tools/mp3-to-midi-feedback/convert-and-analyze', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({ sessionId })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setConversionStatus({ 
          type: 'success', 
          message: `Konversion erfolgreich! ${result.result?.summary?.total_notes || 0} Noten erkannt.` 
        });
        
        // Speichere Konversions-Daten
        localStorage.setItem('mp3ToMidiConversionData', JSON.stringify(result.result));
        
        // Navigate to result page
        setTimeout(() => {
          if (onShowResult) {
            onShowResult();
          }
        }, 1500);
      } else {
        setConversionStatus({ type: 'error', message: result.error || 'Konversion fehlgeschlagen' });
      }
    } catch (error) {
      setConversionStatus({ type: 'error', message: 'Verbindungsfehler bei Konversion' });
      console.error('Conversion error:', error);
    } finally {
      setIsConverting(false);
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>MP3-zu-MIDI: Aufnahmen hochladen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        
        {/* Content Card - shows either upload form or loading state */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {(isUploading || isConverting) ? (
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
                {isUploading ? '📤 Dateien werden hochgeladen...' : '🎹 MIDI-Konvertierung läuft...'}
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                {isUploading 
                  ? 'Deine Audiodateien werden zum Server übertragen' 
                  : 'Basic Pitch analysiert die Audio-Dateien und erstellt MIDI-Dateien. Dies kann bis zu 2 Minuten dauern.'}
              </p>
            </div>
          ) : (
            <>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '50px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Referenz</p>
              <label htmlFor="ref-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="ref-upload" accept="audio/mp3,audio/wav,video/mp4" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['audio/mpeg', 'audio/wav', 'video/mp4', 'audio/mp4'].includes(file.type)) {
                  alert('Nicht unterstützter Dateityp. Bitte wähle MP3, WAV oder MP4.');
                  e.target.value = '';
                  setRefFile(null);
                  setRefFileName('');
                  return;
                }
                setRefFile(file);
                setRefFileName(file?.name || '');
                setUploadStatus(null);
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade die Musik-Datei deiner Lehrkraft hoch!</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach der Musik deiner Lehrkraft. Diese wird zu MIDI konvertiert. Unterstützte Formate: MP3, WAV und MP4</p>
              {refFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{refFileName}</p>}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Dein Song</p>
              <label htmlFor="song-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="song-upload" accept="audio/mp3,audio/wav,video/mp4" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['audio/mpeg', 'audio/wav', 'video/mp4', 'audio/mp4'].includes(file.type)) {
                  alert('Nicht unterstützter Dateityp. Bitte wähle MP3, WAV oder MP4.');
                  e.target.value = '';
                  setStudentFile(null);
                  setStudentFileName('');
                  return;
                }
                setStudentFile(file);
                setStudentFileName(file?.name || '');
                setUploadStatus(null);
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade deine Musik hoch</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach deiner Musik. Diese wird zu MIDI konvertiert. Unterstützte Formate: MP3, WAV und MP4</p>
              {studentFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{studentFileName}</p>}
            </div>
          </div>
        
        {/* Status Messages - inside the else block */}
        {uploadStatus && (
          <div style={{ 
            backgroundColor: 'var(--card-color)',
            borderRadius: '15px', 
            padding: '10px 16px', 
            margin: '20px 0 10px 0', 
            width: '100%',
            border: uploadStatus.type === 'error' ? '2px solid #ff6b6b' : '2px solid transparent',
            borderImage: uploadStatus.type === 'success' ? 'var(--mudiko-gradient) 1' : 'none',
            boxShadow: 'var(--shadow)',
            animation: 'scaleIn 0.4s ease-out',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {uploadStatus.type === 'success' && (
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'var(--mudiko-gradient)',
                opacity: 0.1,
                pointerEvents: 'none'
              }} />
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: uploadStatus.type === 'error' ? '#ff6b6b' : 'var(--mudiko-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white'
              }}>
                {uploadStatus.type === 'error' ? '✕' : '✓'}
              </div>
              
              <p style={{ 
                color: 'var(--font-color)', 
                margin: '0', 
                textAlign: 'center',
                fontWeight: 'var(--button-font-weight)',
                fontSize: 'var(--button-font-size)',
                fontFamily: "'Nunito', sans-serif"
              }}>
                {uploadStatus.message}
              </p>
            </div>
          </div>
        )}

        {conversionStatus && (
          <div style={{ 
            backgroundColor: 'var(--card-color)',
            borderRadius: '15px', 
            padding: '10px 16px', 
            margin: '10px 0', 
            width: '100%',
            border: conversionStatus.type === 'error' ? '2px solid #ff6b6b' : conversionStatus.type === 'info' ? '2px solid #5599ff' : '2px solid transparent',
            borderImage: conversionStatus.type === 'success' ? 'var(--mudiko-gradient) 1' : 'none',
            boxShadow: 'var(--shadow)',
            animation: 'scaleIn 0.4s ease-out',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {conversionStatus.type === 'success' && (
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'var(--mudiko-gradient)',
                opacity: 0.1,
                pointerEvents: 'none'
              }} />
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: conversionStatus.type === 'error' ? '#ff6b6b' : conversionStatus.type === 'info' ? '#5599ff' : 'var(--mudiko-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white'
              }}>
                {conversionStatus.type === 'error' ? '✕' : conversionStatus.type === 'info' ? '⏳' : '✓'}
              </div>
              
              <p style={{ 
                color: 'var(--font-color)', 
                margin: '0', 
                textAlign: 'center',
                fontWeight: 'var(--button-font-weight)',
                fontSize: 'var(--button-font-size)',
                fontFamily: "'Nunito', sans-serif"
              }}>
                {conversionStatus.message}
              </p>
            </div>
          </div>
        )}
          </>
          )}
        </div>
      </div>
      
      {/* Spacing */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '90%', marginBottom: '20px' }}>
        <button
          onClick={() => window.location.href = '/'}
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
            background: (isUploading || isConverting) ? 'var(--button-color)' : 'var(--button-color)',
            border: '2px solid',
            borderImage: (isUploading || isConverting) ? 'none' : 'var(--mudiko-gradient) 1',
            borderColor: (isUploading || isConverting) ? '#999999' : 'transparent',
            color: (isUploading || isConverting) ? '#aaaaaa' : 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '0px',
            cursor: (isUploading || isConverting) ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: (isUploading || isConverting) ? 'none' : 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: (isUploading || isConverting) ? 0.6 : 1,
            transform: (isUploading || isConverting) ? 'scale(0.98)' : 'scale(1)',
            position: 'relative',
            overflow: 'hidden'
          }} 
          onClick={handleUpload}
          disabled={isUploading || isConverting}
          onMouseEnter={(e) => {
            if (!isUploading && !isConverting) {
              e.target.style.transform = 'scale(1.02)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isUploading && !isConverting) {
              e.target.style.transform = 'scale(1)';
            }
          }}
        >
          {(isUploading || isConverting) && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'var(--mudiko-blue)',
              opacity: 0.3,
              animation: 'pulse 1.5s infinite'
            }} />
          )}
          
          <span style={{ position: 'relative', zIndex: 1 }}>
            {isUploading ? '⏳ Hochladen...' : isConverting ? '🎹 Konvertiere zu MIDI...' : '🎹 Hochladen & Konvertieren'}
          </span>
        </button>
      </div>
    </div>
  );
}

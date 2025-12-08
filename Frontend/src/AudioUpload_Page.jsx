// Audio Upload Page with Backend Integration
import { useState } from 'react'

export default function AudioUpload_Page({ onNext }) {
  const [refFile, setRefFile] = useState(null);
  const [songFile, setSongFile] = useState(null);
  const [refFileName, setRefFileName] = useState('');
  const [songFileName, setSongFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleUpload = async () => {
    if (!refFile || !songFile) {
      setUploadStatus({ type: 'error', message: 'Bitte wähle beide Audiodateien aus' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      // Beende ggf. eine vorherige Session
      let sessionId = localStorage.getItem('sessionId');
      if (sessionId) {
        try {
          await fetch('/api/session/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId })
          });
        } catch {}
        localStorage.removeItem('sessionId');
        sessionId = null;
      }

      // Starte eine neue Session
      try {
        const startResp = await fetch('/api/session/start', { method: 'POST' });
        if (startResp.ok) {
          const startJson = await startResp.json();
          sessionId = startJson.sessionId;
          localStorage.setItem('sessionId', sessionId);
        }
      } catch (e) {
        // Fallback: Backend erstellt ggf. automatisch eine Session
      }

      const formData = new FormData();
      formData.append('referenz', refFile);
      formData.append('schueler', songFile);

      const response = await fetch('/api/upload-audio', {
        method: 'POST',
        body: formData,
        headers: sessionId ? { 'X-Session-ID': sessionId } : undefined,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus({ type: 'success', message: 'Dateien erfolgreich hochgeladen!' });
        // Store upload data for next pages
        localStorage.setItem('uploadData', JSON.stringify(result));
        if (result.sessionId) {
          localStorage.setItem('sessionId', result.sessionId);
        }
        // Wait a moment to show success message, then proceed
        setTimeout(() => {
          onNext();
        }, 1500);
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Aufnahmen hochladen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
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
                setUploadStatus(null); // Clear any previous status
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade die Musik-Datei deiner Lehrkraft hoch!</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach der Musik deiner Lehrkraft. Unterstützte Formate sind: MP3, WAV und MP4</p>
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
                  setSongFile(null);
                  setSongFileName('');
                  return;
                }
                setSongFile(file);
                setSongFileName(file?.name || '');
                setUploadStatus(null); // Clear any previous status
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade deine Musik hoch</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach deiner Musik. Unterstützte Formate sind: MP3, WAV und MP4</p>
              {songFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{songFileName}</p>}
            </div>
          </div>
        </div>
        
        {/* Status Message - Redesigned to match app style */}
        {uploadStatus && (
          <div style={{ 
            backgroundColor: 'var(--card-color)',
            borderRadius: '15px', 
            padding: '10px 16px', 
            margin: '10px 0', 
            width: '90%',
            border: uploadStatus.type === 'error' ? '2px solid #ff6b6b' : '2px solid transparent',
            borderImage: uploadStatus.type === 'success' ? 'var(--mudiko-gradient) 1' : 'none',
            boxShadow: 'var(--shadow)',
            animation: 'scaleIn 0.4s ease-out',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Success gradient overlay */}
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
              {/* Icon */}
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
              
              {/* Message */}
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
      </div>
      
      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', width: '95%', marginBottom: '20px' }}>
        <button 
          style={{ 
            background: isUploading ? 'var(--button-color)' : 'var(--button-color)',
            border: '2px solid',
            borderImage: isUploading ? 'none' : 'var(--mudiko-gradient) 1',
            borderColor: isUploading ? '#999999' : 'transparent',
            color: isUploading ? '#aaaaaa' : 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '0px',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: isUploading ? 'none' : 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: isUploading ? 0.6 : 1,
            transform: isUploading ? 'scale(0.98)' : 'scale(1)',
            position: 'relative',
            overflow: 'hidden'
          }} 
          onClick={handleUpload}
          disabled={isUploading}
          onMouseEnter={(e) => {
            if (!isUploading) {
              e.target.style.transform = 'scale(1.02)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isUploading) {
              e.target.style.transform = 'scale(1)';
            }
          }}
        >
          {/* Loading animation overlay */}
          {isUploading && (
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
            {isUploading ? '🎵 Hochladen...' : '🎵 Musik hochladen'}
          </span>
        </button>
      </div>
    </div>
  )
}

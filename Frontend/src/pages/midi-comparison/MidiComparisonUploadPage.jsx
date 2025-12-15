// MIDI Upload Page with Backend Integration
import { useState } from 'react'

export default function MidiUpload_Page({ onNext }) {
  const [refFile, setRefFile] = useState(null);
  const [studentFile, setStudentFile] = useState(null);
  const [refFileName, setRefFileName] = useState('');
  const [studentFileName, setStudentFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleUpload = async () => {
    if (!refFile || !studentFile) {
      setUploadStatus({ type: 'error', message: 'Bitte wähle beide MIDI-Dateien aus' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      // Beende ggf. eine vorherige Session
      let sessionId = sessionStorage.getItem('midiSessionId');
      if (sessionId) {
        try {
          await fetch('/api/tools/midi-comparison/session/cleanup', {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'X-Session-ID': sessionId
            }
          });
        } catch {}
        sessionStorage.removeItem('midiSessionId');
        sessionId = null;
      }

      // Starte eine neue Session
      try {
        const startResp = await fetch('/api/session/start', { method: 'POST' });
        if (startResp.ok) {
          const startJson = await startResp.json();
          sessionId = startJson.sessionId;
          sessionStorage.setItem('midiSessionId', sessionId);
        }
      } catch (e) {
        // Fallback: Backend erstellt ggf. automatisch eine Session
      }

      const formData = new FormData();
      formData.append('referenz', refFile);
      formData.append('schueler', studentFile);

      const response = await fetch('/api/tools/midi-comparison/upload', {
        method: 'POST',
        body: formData,
        headers: sessionId ? { 'X-Session-ID': sessionId } : undefined,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus({ type: 'success', message: 'MIDI-Dateien erfolgreich hochgeladen!' });
        // Store upload data for next pages
        sessionStorage.setItem('midiUploadData', JSON.stringify(result));
        if (result.sessionId) {
          sessionStorage.setItem('midiSessionId', result.sessionId);
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>MIDI-Dateien hochladen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '50px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Referenz</p>
              <label htmlFor="ref-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="ref-upload" accept=".mid,.midi" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['.mid', '.midi'].some(ext => file.name.toLowerCase().endsWith(ext))) {
                  alert('Nicht unterstützter Dateityp. Bitte wähle MID oder MIDI.');
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
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade die MIDI-Datei deiner Lehrkraft hoch!</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach der MIDI deiner Lehrkraft. Unterstützte Formate sind: MID und MIDI</p>
              {refFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{refFileName}</p>}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Deine MIDI</p>
              <label htmlFor="student-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="student-upload" accept=".mid,.midi" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['.mid', '.midi'].some(ext => file.name.toLowerCase().endsWith(ext))) {
                  alert('Nicht unterstützter Dateityp. Bitte wähle MID oder MIDI.');
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
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade deine MIDI hoch</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach deiner MIDI. Unterstützte Formate sind: MID und MIDI</p>
              {studentFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{studentFileName}</p>}
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
                fontSize: '15px',
                fontWeight: '500'
              }}>
                {uploadStatus.message}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <div style={{ 
        width: '90%', 
        display: 'flex', 
        justifyContent: 'space-between', 
        marginBottom: '20px' 
      }}>
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
          onClick={handleUpload}
          disabled={isUploading || !refFile || !studentFile}
          style={{
            backgroundColor: (!refFile || !studentFile) ? 'gray' : 'var(--button-color)',
            border: '3px solid',
            borderImage: (!refFile || !studentFile) ? 'none' : 'var(--mudiko-gradient) 1',
            borderColor: (!refFile || !studentFile) ? 'gray' : 'transparent',
            color: 'var(--font-color)',
            padding: '12px 30px',
            borderRadius: '0',
            fontFamily: "'Nunito', sans-serif",
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: (!refFile || !studentFile || isUploading) ? 'not-allowed' : 'pointer',
            transition: 'transform 0.2s ease',
            opacity: (!refFile || !studentFile) ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (refFile && studentFile && !isUploading) {
              e.target.style.transform = 'scale(1.05)';
            }
          }}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          {isUploading ? 'Wird hochgeladen...' : 'Weiter →'}
        </button>
      </div>
    </div>
  );
}

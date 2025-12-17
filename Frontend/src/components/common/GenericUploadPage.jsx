// Generic Upload Page - Reusable component for all upload workflows
import { useState } from 'react'

export default function GenericUploadPage({
  title,
  refLabel = 'Referenz',
  refDescription,
  studentLabel = 'Dein Song',
  studentDescription,
  acceptedFormats,
  acceptedMimeTypes = [],
  formatDescription,
  uploadApiEndpoint,
  cleanupApiEndpoint,
  sessionStorageKey,
  uploadDataStorageKey,
  errorMessage = 'Bitte wähle beide Dateien aus',
  successMessage = 'Dateien erfolgreich hochgeladen!',
  onNext,
  onBack
}) {
  const [refFile, setRefFile] = useState(null);
  const [studentFile, setStudentFile] = useState(null);
  const [refFileName, setRefFileName] = useState('');
  const [studentFileName, setStudentFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const validateFileType = (file, accept, mimeTypes) => {
    if (accept && accept.startsWith('.')) {
      // File extension check
      const extensions = accept.split(',').map(ext => ext.trim().toLowerCase());
      return extensions.some(ext => file.name.toLowerCase().endsWith(ext));
    } else if (mimeTypes && mimeTypes.length > 0) {
      // MIME type check
      return mimeTypes.includes(file.type);
    }
    return true;
  };

  const handleFileSelect = (file, isRef) => {
    if (!validateFileType(file, acceptedFormats, acceptedMimeTypes)) {
      alert(`Nicht unterstützter Dateityp. Bitte wähle ${formatDescription}.`);
      return null;
    }
    return file;
  };

  const handleUpload = async () => {
    if (!refFile || !studentFile) {
      setUploadStatus({ type: 'error', message: errorMessage });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      // Cleanup alte Session
      let sessionId = localStorage.getItem(sessionStorageKey) || sessionStorage.getItem(sessionStorageKey);
      if (sessionId && cleanupApiEndpoint) {
        try {
          await fetch(cleanupApiEndpoint, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'X-Session-ID': sessionId
            },
            body: JSON.stringify({ sessionId })
          });
        } catch {}
        localStorage.removeItem(sessionStorageKey);
        sessionStorage.removeItem(sessionStorageKey);
        sessionId = null;
      }

      // Upload
      const formData = new FormData();
      formData.append('referenz', refFile);
      formData.append('schueler', studentFile);

      const response = await fetch(uploadApiEndpoint, {
        method: 'POST',
        body: formData,
        headers: sessionId ? { 'X-Session-ID': sessionId } : {},
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus({ type: 'success', message: successMessage });
        
        // Store data
        if (result.sessionId) {
          if (sessionStorageKey === 'midiSessionId') {
            sessionStorage.setItem(sessionStorageKey, result.sessionId);
          } else {
            localStorage.setItem(sessionStorageKey, result.sessionId);
          }
        }
        
        if (uploadDataStorageKey) {
          if (sessionStorageKey === 'midiSessionId') {
            sessionStorage.setItem(uploadDataStorageKey, JSON.stringify(result));
          } else {
            localStorage.setItem(uploadDataStorageKey, JSON.stringify(result));
          }
        }
        
        // Navigate to next page
        setTimeout(() => {
          if (onNext) {
            onNext();
          }
        }, 1000);
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
        {/* Header */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>{title}</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        {/* Content Card */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {isUploading ? (
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
                📤 Dateien werden hochgeladen...
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                Deine Dateien werden zum Server übertragen
              </p>
            </div>
          ) : (
            <>
              {/* Referenz File */}
              <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '50px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
                  <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>{refLabel}</p>
                  <label htmlFor="ref-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
                  <input 
                    type="file" 
                    id="ref-upload" 
                    accept={acceptedFormats} 
                    style={{ display: 'none' }} 
                    onChange={(e) => {
                      const file = e.target.files[0];
                      const validFile = file ? handleFileSelect(file, true) : null;
                      if (validFile) {
                        setRefFile(file);
                        setRefFileName(file.name);
                        setUploadStatus(null);
                      } else {
                        e.target.value = '';
                        setRefFile(null);
                        setRefFileName('');
                      }
                    }} 
                  />
                </div>
                <div style={{ marginLeft: '20px', flex: 1 }}>
                  <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>{refDescription}</p>
                  <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>
                    Tippe auf das "+" und suche in deinen Dateien nach der Datei deiner Lehrkraft. Unterstützte Formate: {formatDescription}
                  </p>
                  {refFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{refFileName}</p>}
                </div>
              </div>

              {/* Student File */}
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
                  <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>{studentLabel}</p>
                  <label htmlFor="student-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
                  <input 
                    type="file" 
                    id="student-upload" 
                    accept={acceptedFormats} 
                    style={{ display: 'none' }} 
                    onChange={(e) => {
                      const file = e.target.files[0];
                      const validFile = file ? handleFileSelect(file, false) : null;
                      if (validFile) {
                        setStudentFile(file);
                        setStudentFileName(file.name);
                        setUploadStatus(null);
                      } else {
                        e.target.value = '';
                        setStudentFile(null);
                        setStudentFileName('');
                      }
                    }} 
                  />
                </div>
                <div style={{ marginLeft: '20px', flex: 1 }}>
                  <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>{studentDescription}</p>
                  <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>
                    Tippe auf das "+" und suche in deinen Dateien nach deiner Datei. Unterstützte Formate: {formatDescription}
                  </p>
                  {studentFileName && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{studentFileName}</p>}
                </div>
              </div>

              {/* Status Message */}
              {uploadStatus && (
                <div style={{ 
                  backgroundColor: 'var(--card-color)',
                  borderRadius: '15px', 
                  padding: '10px 16px', 
                  margin: '20px 0 0 0', 
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
                      fontSize: '15px',
                      fontWeight: '500'
                    }}>
                      {uploadStatus.message}
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

      {/* Bottom Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '90%', marginBottom: '20px' }}>
        <button
          onClick={onBack || (() => window.location.href = '/')}
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
            border: '2px solid',
            borderImage: (!refFile || !studentFile || isUploading) ? 'none' : 'var(--mudiko-gradient) 1',
            borderColor: (!refFile || !studentFile || isUploading) ? '#999999' : 'transparent',
            color: (!refFile || !studentFile || isUploading) ? '#aaaaaa' : 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '0px',
            cursor: (!refFile || !studentFile || isUploading) ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: (!refFile || !studentFile || isUploading) ? 'none' : 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: (!refFile || !studentFile || isUploading) ? 0.6 : 1,
            transform: isUploading ? 'scale(0.98)' : 'scale(1)',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseEnter={(e) => {
            if (refFile && studentFile && !isUploading) {
              e.target.style.transform = 'scale(1.02)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isUploading) {
              e.target.style.transform = 'scale(1)';
            }
          }}
        >
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
            {isUploading ? '⏳ Hochladen...' : '📤 Hochladen'}
          </span>
        </button>
      </div>
    </div>
  );
}

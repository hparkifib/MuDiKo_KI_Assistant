import { useState, useRef, useEffect } from 'react'

export default function EasyFeedbackUploadPage({ onNext, onBack }) {
  // File states
  const [refFile, setRefFile] = useState(null);
  const [refFileName, setRefFileName] = useState('');
  const [refAudioUrl, setRefAudioUrl] = useState(null);
  
  const [studentFile, setStudentFile] = useState(null);
  const [studentFileName, setStudentFileName] = useState('');
  const [studentAudioUrl, setStudentAudioUrl] = useState(null);
  
  // Recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [showRecordingSection, setShowRecordingSection] = useState(false);
  
  // Upload states
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  
  // Refs
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  const acceptedFormats = ".mp3,.wav,.mid,.midi,.webm,.ogg";
  const acceptedMimeTypes = [
    'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav', 
    'audio/midi', 'audio/x-midi', 'audio/mid',
    'audio/webm', 'audio/ogg'
  ];

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (refAudioUrl) URL.revokeObjectURL(refAudioUrl);
      if (studentAudioUrl && !studentAudioUrl.startsWith('data:')) URL.revokeObjectURL(studentAudioUrl);
    };
  }, []);

  const validateFileType = (file) => {
    const ext = file.name.toLowerCase().split('.').pop();
    const validExtensions = ['mp3', 'wav', 'mid', 'midi', 'webm', 'ogg'];
    if (validExtensions.includes(ext)) return true;
    return acceptedMimeTypes.includes(file.type);
  };

  const isMidiFile = (file) => {
    const ext = file.name.toLowerCase().split('.').pop();
    return ['mid', 'midi'].includes(ext);
  };

  const handleRefFileChange = (e) => {
    const file = e.target.files[0];
    if (file && validateFileType(file)) {
      setRefFile(file);
      setRefFileName(file.name);
      setUploadStatus(null);
      
      // Create audio URL for playback (only for audio files, not MIDI)
      if (!isMidiFile(file)) {
        if (refAudioUrl) URL.revokeObjectURL(refAudioUrl);
        setRefAudioUrl(URL.createObjectURL(file));
      } else {
        setRefAudioUrl(null);
      }
    } else if (file) {
      alert('Nicht unterstützter Dateityp. Bitte wähle MP3, WAV oder MIDI.');
      e.target.value = '';
    }
  };

  const handleStudentFileChange = (e) => {
    const file = e.target.files[0];
    if (file && validateFileType(file)) {
      setStudentFile(file);
      setStudentFileName(file.name);
      setUploadStatus(null);
      setShowRecordingSection(false);
      
      if (!isMidiFile(file)) {
        if (studentAudioUrl) URL.revokeObjectURL(studentAudioUrl);
        setStudentAudioUrl(URL.createObjectURL(file));
      } else {
        setStudentAudioUrl(null);
      }
    } else if (file) {
      alert('Nicht unterstützter Dateityp. Bitte wähle MP3, WAV oder MIDI.');
      e.target.value = '';
    }
  };

  // Recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        const file = new File([blob], 'Meine_Aufnahme.webm', { type: 'audio/webm' });
        
        setStudentFile(file);
        setStudentFileName('Meine_Aufnahme.webm');
        setStudentAudioUrl(url);
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Recording error:', error);
      setUploadStatus({ 
        type: 'error', 
        message: 'Mikrofon-Zugriff verweigert. Bitte erlaube den Zugriff in deinem Browser.' 
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const clearRefFile = () => {
    if (refAudioUrl) URL.revokeObjectURL(refAudioUrl);
    setRefFile(null);
    setRefFileName('');
    setRefAudioUrl(null);
  };

  const clearStudentFile = () => {
    if (studentAudioUrl) URL.revokeObjectURL(studentAudioUrl);
    setStudentFile(null);
    setStudentFileName('');
    setStudentAudioUrl(null);
  };

  const handleUpload = async () => {
    if (!refFile || !studentFile) {
      setUploadStatus({ type: 'error', message: 'Bitte wähle beide Dateien aus.' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      // Create session
      const sessionResponse = await fetch('/api/tools/easy-feedback/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const sessionResult = await sessionResponse.json();
      
      if (!sessionResult.success) {
        throw new Error(sessionResult.error || 'Session-Erstellung fehlgeschlagen');
      }
      
      const sessionId = sessionResult.sessionId;
      localStorage.setItem('easyFeedbackSessionId', sessionId);

      // Upload Reference
      const refFormData = new FormData();
      refFormData.append('file', refFile);
      refFormData.append('role', 'referenz');

      const refResponse = await fetch('/api/tools/easy-feedback/upload', {
        method: 'POST',
        headers: { 'X-Session-ID': sessionId },
        body: refFormData
      });
      const refResult = await refResponse.json();

      if (!refResult.success) {
        throw new Error(refResult.error || 'Referenz-Upload fehlgeschlagen');
      }

      // Upload Student
      const studentFormData = new FormData();
      studentFormData.append('file', studentFile);
      studentFormData.append('role', 'schueler');

      const studentResponse = await fetch('/api/tools/easy-feedback/upload', {
        method: 'POST',
        headers: { 'X-Session-ID': sessionId },
        body: studentFormData
      });
      const studentResult = await studentResponse.json();

      if (!studentResult.success) {
        throw new Error(studentResult.error || 'Schüler-Upload fehlgeschlagen');
      }

      setUploadStatus({ type: 'success', message: 'Dateien erfolgreich hochgeladen!' });

      setTimeout(() => {
        if (onNext) onNext();
      }, 1000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ type: 'error', message: error.message || 'Verbindungsfehler zum Server' });
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
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, overflow: 'auto' }}>
        {/* Header */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Easy Feedback</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        {/* Content Card */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px', marginBottom: '20px' }}>
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
            </div>
          ) : (
            <>
              {/* ===== REFERENZ SECTION ===== */}
              <div style={{ 
                backgroundColor: 'rgba(135, 189, 207, 0.1)',
                borderRadius: '15px',
                padding: '20px',
                marginBottom: '20px',
                border: '2px solid var(--mudiko-cyan)'
              }}>
                <h3 style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '18px' }}>
                  🎵 Referenz-Audio
                </h3>
                
                {!refFile ? (
                  <>
                    <p style={{ color: 'var(--font-color)', opacity: 0.8, margin: '0 0 15px 0', fontSize: '14px' }}>
                      Das Musik-Beispiel von deiner Lehrkraft
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flexWrap: 'wrap' }}>
                      <label htmlFor="ref-upload" style={{ 
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        backgroundColor: 'var(--button-color)', 
                        border: '2px solid var(--mudiko-cyan)',
                        padding: '10px 20px',
                        borderRadius: '10px',
                        cursor: 'pointer',
                        fontFamily: "'Nunito', sans-serif",
                        fontSize: '14px',
                        color: 'var(--font-color)'
                      }}>
                        📁 Datei wählen
                      </label>
                      <input 
                        type="file" 
                        id="ref-upload" 
                        accept={acceptedFormats} 
                        style={{ display: 'none' }} 
                        onChange={handleRefFileChange}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                      <span style={{ color: 'var(--mudiko-cyan)', fontSize: '14px' }}>
                        ✓ {refFileName}
                      </span>
                      <button
                        onClick={clearRefFile}
                        style={{
                          backgroundColor: 'transparent',
                          color: '#ff6b6b',
                          border: '1px solid #ff6b6b',
                          padding: '4px 10px',
                          borderRadius: '5px',
                          cursor: 'pointer',
                          fontFamily: "'Nunito', sans-serif",
                          fontSize: '12px'
                        }}
                      >
                        ✕ Entfernen
                      </button>
                    </div>
                    
                    {/* Reference Audio Player */}
                    {refAudioUrl && (
                      <audio controls src={refAudioUrl} style={{ width: '100%' }} />
                    )}
                    
                    {isMidiFile(refFile) && (
                      <p style={{ color: 'var(--mudiko-cyan)', fontSize: '13px', margin: '10px 0 0 0' }}>
                        ℹ️ MIDI-Dateien können nicht abgespielt werden
                      </p>
                    )}
                  </>
                )}
              </div>

              {/* ===== SCHÜLER SECTION ===== */}
              <div style={{ 
                backgroundColor: 'rgba(255, 158, 161, 0.1)',
                borderRadius: '15px',
                padding: '20px',
                marginBottom: '20px',
                border: '2px solid var(--mudiko-pink)'
              }}>
                <h3 style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '18px' }}>
                  🎤 Deine Aufnahme
                </h3>
                
                {!studentFile && !showRecordingSection && (
                  <>
                    <p style={{ color: 'var(--font-color)', opacity: 0.8, margin: '0 0 15px 0', fontSize: '14px' }}>
                      Deine eigene Version des Musikstücks
                    </p>
                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                      <label htmlFor="student-upload" style={{ 
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        backgroundColor: 'var(--button-color)', 
                        border: '2px solid var(--mudiko-pink)',
                        padding: '10px 20px',
                        borderRadius: '10px',
                        cursor: 'pointer',
                        fontFamily: "'Nunito', sans-serif",
                        fontSize: '14px',
                        color: 'var(--font-color)'
                      }}>
                        📁 Datei wählen
                      </label>
                      <input 
                        type="file" 
                        id="student-upload" 
                        accept={acceptedFormats} 
                        style={{ display: 'none' }} 
                        onChange={handleStudentFileChange}
                      />
                      
                      <button
                        onClick={() => setShowRecordingSection(true)}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '8px',
                          backgroundColor: 'var(--button-color)', 
                          border: '2px solid var(--mudiko-pink)',
                          padding: '10px 20px',
                          borderRadius: '10px',
                          cursor: 'pointer',
                          fontFamily: "'Nunito', sans-serif",
                          fontSize: '14px',
                          color: 'var(--font-color)'
                        }}
                      >
                        🎙️ Jetzt aufnehmen
                      </button>
                    </div>
                  </>
                )}

                {/* Recording Section */}
                {showRecordingSection && !studentFile && (
                  <div style={{ 
                    backgroundColor: 'var(--button-color)',
                    borderRadius: '10px',
                    padding: '20px',
                    textAlign: 'center'
                  }}>
                    {isRecording ? (
                      <>
                        <div style={{ fontSize: '50px', marginBottom: '10px', animation: 'pulse 1s infinite' }}>🔴</div>
                        <p style={{ color: 'var(--font-color)', fontSize: '24px', margin: '0 0 15px 0', fontWeight: '600' }}>
                          {formatTime(recordingTime)}
                        </p>
                        <button
                          onClick={stopRecording}
                          style={{
                            backgroundColor: '#ff6b6b',
                            color: 'white',
                            border: 'none',
                            padding: '12px 30px',
                            borderRadius: '20px',
                            cursor: 'pointer',
                            fontFamily: "'Nunito', sans-serif",
                            fontSize: '16px',
                            fontWeight: '600'
                          }}
                        >
                          ⏹ Aufnahme beenden
                        </button>
                      </>
                    ) : (
                      <>
                        <div style={{ fontSize: '50px', marginBottom: '10px' }}>🎤</div>
                        <p style={{ color: 'var(--font-color)', margin: '0 0 15px 0' }}>
                          Bereit zur Aufnahme
                        </p>
                        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                          <button
                            onClick={startRecording}
                            style={{
                              backgroundColor: 'var(--mudiko-pink)',
                              color: 'white',
                              border: 'none',
                              padding: '12px 30px',
                              borderRadius: '20px',
                              cursor: 'pointer',
                              fontFamily: "'Nunito', sans-serif",
                              fontSize: '16px',
                              fontWeight: '600'
                            }}
                          >
                            ⏺ Start
                          </button>
                          <button
                            onClick={() => setShowRecordingSection(false)}
                            style={{
                              backgroundColor: 'transparent',
                              color: 'var(--font-color)',
                              border: '1px solid #666',
                              padding: '12px 20px',
                              borderRadius: '20px',
                              cursor: 'pointer',
                              fontFamily: "'Nunito', sans-serif",
                              fontSize: '14px'
                            }}
                          >
                            Abbrechen
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}

                {/* Student File Selected */}
                {studentFile && (
                  <>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                      <span style={{ color: 'var(--mudiko-pink)', fontSize: '14px' }}>
                        ✓ {studentFileName}
                      </span>
                      <button
                        onClick={clearStudentFile}
                        style={{
                          backgroundColor: 'transparent',
                          color: '#ff6b6b',
                          border: '1px solid #ff6b6b',
                          padding: '4px 10px',
                          borderRadius: '5px',
                          cursor: 'pointer',
                          fontFamily: "'Nunito', sans-serif",
                          fontSize: '12px'
                        }}
                      >
                        ✕ Entfernen
                      </button>
                    </div>
                    
                    {/* Student Audio Player */}
                    {studentAudioUrl && (
                      <audio controls src={studentAudioUrl} style={{ width: '100%' }} />
                    )}
                    
                    {studentFile && isMidiFile(studentFile) && (
                      <p style={{ color: 'var(--mudiko-pink)', fontSize: '13px', margin: '10px 0 0 0' }}>
                        ℹ️ MIDI-Dateien können nicht abgespielt werden
                      </p>
                    )}
                  </>
                )}
              </div>

              {/* Status Message */}
              {uploadStatus && (
                <div style={{ 
                  padding: '15px',
                  borderRadius: '10px',
                  backgroundColor: uploadStatus.type === 'error' ? 'rgba(255, 107, 107, 0.1)' : 'rgba(72, 187, 120, 0.1)',
                  border: `2px solid ${uploadStatus.type === 'error' ? '#ff6b6b' : '#48bb78'}`,
                  marginBottom: '20px'
                }}>
                  <p style={{ 
                    color: uploadStatus.type === 'error' ? '#ff6b6b' : '#48bb78',
                    margin: '0',
                    textAlign: 'center'
                  }}>
                    {uploadStatus.type === 'error' ? '⚠️' : '✅'} {uploadStatus.message}
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '95%', padding: '20px 0', flexShrink: 0 }}>
        <button 
          onClick={onBack}
          disabled={isRecording}
          style={{
            backgroundColor: 'var(--button-color)',
            color: 'var(--font-color)',
            border: '2px solid #666666',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: isRecording ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'transform 0.3s ease, opacity 0.3s ease',
            opacity: isRecording ? 0.5 : 1
          }}
          onMouseEnter={(e) => { if (!isRecording) e.target.style.transform = 'scale(1.02)' }}
          onMouseLeave={(e) => { if (!isRecording) e.target.style.transform = 'scale(1)' }}
        >
          ← Zurück
        </button>
        
        <button 
          onClick={handleUpload}
          disabled={!refFile || !studentFile || isRecording}
          style={{ 
            backgroundColor: 'var(--button-color)',
            border: '3px solid', 
            borderImage: 'var(--mudiko-gradient) 1',
            color: 'var(--font-color)',
            padding: '15px 30px',
            borderRadius: '0px',
            cursor: (!refFile || !studentFile || isRecording) ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'transform 0.3s ease, opacity 0.3s ease',
            letterSpacing: '1px',
            opacity: (!refFile || !studentFile || isRecording) ? 0.5 : 1
          }}
          onMouseEnter={(e) => { if (refFile && studentFile && !isRecording) e.target.style.transform = 'scale(1.05)' }}
          onMouseLeave={(e) => { if (refFile && studentFile && !isRecording) e.target.style.transform = 'scale(1)' }}
        >
          Hochladen
        </button>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}

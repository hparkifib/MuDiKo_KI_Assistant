import { useState, useEffect } from 'react'

export default function PromptPage({ onBack }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState(null);
  const [uploadData, setUploadData] = useState(null);
  const [showPromptModal, setShowPromptModal] = useState(false);

  useEffect(() => {
    // Load all data and start generation automatically
    try {
      const savedFormData = JSON.parse(localStorage.getItem('formData') || '{}');
      const savedUploadData = JSON.parse(localStorage.getItem('uploadData') || '{}');
      
      setFormData(savedFormData);
      setUploadData(savedUploadData);
      
      // Start generating feedback automatically
      generateFeedback(savedFormData, savedUploadData);
    } catch (error) {
      setError('Fehler beim Laden der gespeicherten Daten');
      console.error('Error loading data:', error);
    }
  }, []);

  const generateFeedback = async (formData, uploadData) => {
    if (!formData || !uploadData) {
      setError('Unvollständige Daten. Bitte gehen Sie zurück und füllen Sie alle Schritte aus.');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Prepare request data for backend
      const requestData = {
        language: formData.language || 'deutsch',
        customLanguage: formData.customLanguage || '',
        referenzInstrument: formData.referenceInstrument || 'keine Angabe',
        schuelerInstrument: formData.userInstrument || 'keine Angabe',
        topics: formData.topics || [],
        prompt_type: 'contextual',
        use_simple_language: formData.simpleLanguage || false,
        personalMessage: formData.personalMessage || ''
      };

      console.log('Sending request to backend:', requestData);

      const sessionId = (uploadData && uploadData.sessionId) || localStorage.getItem('sessionId');
      const response = await fetch('/api/generate-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(sessionId ? { 'X-Session-ID': sessionId } : {})
        },
        body: JSON.stringify({ ...requestData, ...(sessionId ? { sessionId } : {}) }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setGeneratedPrompt(result.system_prompt);
        setAnalysisData(result.analysis_data);
        if (result.sessionId) {
          localStorage.setItem('sessionId', result.sessionId);
        }
      } else {
        setError(result.error || 'Fehler bei der Feedback-Generierung');
      }
    } catch (error) {
      setError('Verbindungsfehler zum Server. Ist der Backend-Server gestartet?');
      console.error('Feedback generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    const button = document.getElementById('copy-button');
    const originalText = button.textContent;
    
    // Schritt 1: Moderne Clipboard API versuchen
    try {
      // Prüfen ob Clipboard API verfügbar ist
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(generatedPrompt);
        
        // Erfolg - visuelles Feedback
        button.textContent = '✓ Kopiert!';
        button.style.backgroundColor = 'var(--mudiko-pink)';
        button.style.border = '3px solid var(--mudiko-pink)';
        button.style.borderImage = 'none';
        
        setTimeout(() => {
          button.textContent = originalText;
          button.style.backgroundColor = 'var(--button-color)';
          button.style.border = '3px solid';
          button.style.borderImage = 'var(--mudiko-gradient) 1';
        }, 2000);
        
        return; // Erfolgreich beendet
      }
    } catch (error) {
      console.log('Clipboard API fehlgeschlagen, versuche Fallback:', error);
    }
    
    // Schritt 2: execCommand Fallback (funktioniert auf mehr Geräten)
    try {
      const textArea = document.createElement('textarea');
      textArea.value = generatedPrompt;
      
      // Wichtig für mobile Geräte: Textarea sichtbar aber außerhalb des Viewports
      textArea.style.position = 'fixed';
      textArea.style.top = '0';
      textArea.style.left = '0';
      textArea.style.width = '2em';
      textArea.style.height = '2em';
      textArea.style.padding = '0';
      textArea.style.border = 'none';
      textArea.style.outline = 'none';
      textArea.style.boxShadow = 'none';
      textArea.style.background = 'transparent';
      textArea.style.fontSize = '16px'; // Wichtig für iOS: verhindert Zoom
      
      document.body.appendChild(textArea);
      
      // Fokussieren und auswählen
      textArea.focus();
      textArea.select();
      textArea.setSelectionRange(0, textArea.value.length);
      
      // Kopieren
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (successful) {
        // Erfolg - visuelles Feedback
        button.textContent = '✓ Kopiert!';
        button.style.backgroundColor = 'var(--mudiko-pink)';
        button.style.border = '3px solid var(--mudiko-pink)';
        button.style.borderImage = 'none';
        
        setTimeout(() => {
          button.textContent = originalText;
          button.style.backgroundColor = 'var(--button-color)';
          button.style.border = '3px solid';
          button.style.borderImage = 'var(--mudiko-gradient) 1';
        }, 2000);
        
        return; // Erfolgreich beendet
      }
    } catch (error) {
      console.log('execCommand fehlgeschlagen:', error);
    }
    
    // Schritt 3: Wenn alles fehlschlägt - Benutzer informieren
    button.textContent = '❌ Kopieren nicht möglich';
    button.style.backgroundColor = '#ff6b6b';
    button.style.border = '3px solid #ff6b6b';
    button.style.borderImage = 'none';
    
    // Tipp für den Benutzer
    setTimeout(() => {
      alert('Kopieren automatisch nicht möglich.\n\nTipp: Drücke "Prompt anzeigen" und wähle den Text manuell aus.');
      
      button.textContent = originalText;
      button.style.backgroundColor = 'var(--button-color)';
      button.style.border = '3px solid';
      button.style.borderImage = 'var(--mudiko-gradient) 1';
    }, 1000);
  };

  const copyToClipboardFromModal = async () => {
    const button = document.getElementById('modal-copy-button');
    const originalText = button.textContent;
    
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      
      // Visual feedback for modal button
      button.textContent = '✓ Kopiert!';
      button.style.backgroundColor = 'var(--mudiko-pink)';
      button.style.border = '3px solid var(--mudiko-pink)';
      button.style.borderImage = 'none';
      
      setTimeout(() => {
        button.textContent = originalText;
        button.style.backgroundColor = 'var(--button-color)';
        button.style.border = '3px solid';
        button.style.borderImage = 'var(--mudiko-gradient) 1';
      }, 2000);
      
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = generatedPrompt;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      
      button.textContent = '✓ Kopiert!';
      button.style.backgroundColor = 'var(--mudiko-pink)';
      button.style.border = '3px solid var(--mudiko-pink)';
      button.style.borderImage = 'none';
      
      setTimeout(() => {
        button.textContent = originalText;
        button.style.backgroundColor = 'var(--button-color)';
        button.style.border = '3px solid';
        button.style.borderImage = 'var(--mudiko-gradient) 1';
      }, 2000);
    }
  };

  const handleNewFeedback = () => {
    // End session explicitly, then clear state
    const sid = localStorage.getItem('sessionId');
    if (sid) {
      // Fire and forget; don't block UI
      fetch('/api/session/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId: sid }),
        keepalive: true
      }).catch(() => {});
    }

    // Clear all stored data
    localStorage.removeItem('formData');
    localStorage.removeItem('uploadData');
    localStorage.removeItem('sessionId');
    onBack();
  };

  // Try to end the session if the user leaves this page
  useEffect(() => {
    const handleBeforeUnload = () => {
      const sid = localStorage.getItem('sessionId');
      if (!sid) return;
      try {
        navigator.sendBeacon('/api/session/end', new Blob([JSON.stringify({ sessionId: sid })], { type: 'application/json' }));
      } catch (e) {
        // Fallback best-effort
        fetch('/api/session/end', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sessionId: sid }),
          keepalive: true
        }).catch(() => {});
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const downloadAnalysisData = () => {
    if (!analysisData) return;

    // Erstelle Blob aus Text-String
    const blob = new Blob([analysisData], { type: 'text/plain; charset=utf-8' });
    
    // Erstelle Download-Link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Hole den Schüler-Dateinamen aus uploadData
    let schuelerName = 'schueler-analyse';
    if (uploadData && uploadData.original_filenames && uploadData.original_filenames.schueler) {
      // Entferne die Dateiendung (.mp3, .wav, etc.)
      schuelerName = uploadData.original_filenames.schueler.replace(/\.[^/.]+$/, '');
      // Ersetze Leerzeichen und Sonderzeichen mit Unterstrich
      schuelerName = schuelerName.replace(/[^a-zA-Z0-9-_äöüÄÖÜß]/g, '_');
    }
    
    // Dateiname mit Schüler-Namen und Zeitstempel
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    link.download = `${schuelerName}_Audio-Daten_${timestamp}.txt`;
    
    // Trigger Download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ 
      height: '100vh', /* Fallback für ältere Browser */
      height: '100dvh', /* Dynamic Viewport Height - berücksichtigt Toolbar */
      width: '100%', 
      backgroundColor: 'var(--bg-color)', 
      backgroundImage: 'url(/Rainbow-Line.svg)', 
      backgroundPosition: 'top', 
      backgroundRepeat: 'no-repeat', 
      backgroundSize: 'contain', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center' 
    }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, justifyContent: 'flex-start', minHeight: '0', overflow: 'auto' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback Prompt</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px', marginBottom: '20px' }}>
          {isGenerating ? (
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
                🎵 Deine Audio-Dateien werden analysiert...
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                Deine Musik wird analysiert, um einen persönlichen Feedback-Prompt für eine KI zu erstellen.
              </p>
            </div>
          ) : error ? (
            <div style={{ 
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              borderRadius: '15px', 
              padding: '25px',
              border: '2px solid #ff6b6b',
              textAlign: 'center'
            }}>
              <h3 style={{ color: '#ff6b6b', margin: '0 0 15px 0', fontSize: '18px' }}>
                ⚠️ Fehler beim Generieren
              </h3>
              <p style={{ color: '#ff6b6b', margin: '0 0 20px 0', fontWeight: '500' }}>
                {error}
              </p>
              <button
                onClick={() => generateFeedback(formData, uploadData)}
                style={{
                  backgroundColor: '#ff6b6b',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontFamily: "'Nunito', sans-serif",
                  fontWeight: '600'
                }}
              >
                🔄 Erneut versuchen
              </button>
            </div>
          ) : generatedPrompt ? (
            <>
              <div style={{ marginBottom: '25px' }}>
                <h3 style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '20px' }}>
                  🎉 Dein personalisiertes Feedback ist vorbereitet!
                </h3>
              </div>

              {/* Action Buttons nebeneinander */}
              <div style={{ display: 'flex', justifyContent: 'center', gap: '15px', marginBottom: '20px', flexWrap: 'wrap' }}>
                <button
                  onClick={() => setShowPromptModal(true)}
                  style={{
                    backgroundColor: 'var(--button-color)',
                    border: '2px solid #666666',
                    color: 'var(--font-color)',
                    padding: '12px 20px',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    fontFamily: "'Nunito', sans-serif",
                    fontSize: 'var(--button-font-size)',
                    fontWeight: 'var(--button-font-weight)',
                    boxShadow: 'var(--shadow)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                >
                  📝 Prompt anzeigen
                </button>
                
                <button 
                  id="copy-button"
                  onClick={copyToClipboard}
                  style={{ 
                    backgroundColor: 'var(--button-color)',
                    border: '3px solid', 
                    borderImage: 'var(--mudiko-gradient) 1',
                    color: 'var(--font-color)',
                    padding: '15px 30px',
                    borderRadius: '0px',
                    cursor: 'pointer',
                    fontFamily: "'Nunito', sans-serif",
                    fontSize: 'var(--button-font-size)',
                    fontWeight: 'var(--button-font-weight)',
                    boxShadow: 'var(--shadow)',
                    transition: 'all 0.3s ease',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                >
                  📋 Prompt kopieren
                </button>

                <button
                  onClick={downloadAnalysisData}
                  style={{
                    backgroundColor: 'var(--button-color)',
                    border: '3px solid',
                    borderImage: 'var(--mudiko-gradient) 1',
                    color: 'var(--font-color)',
                    padding: '15px 30px',
                    borderRadius: '0px',
                    cursor: 'pointer',
                    fontFamily: "'Nunito', sans-serif",
                    fontSize: 'var(--button-font-size)',
                    fontWeight: 'var(--button-font-weight)',
                    boxShadow: 'var(--shadow)',
                    transition: 'all 0.3s ease',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                >
                  💾 Analyse-Daten herunterladen
                </button>
              </div>

              {/* Usage Instructions */}
              <div style={{
                backgroundColor: 'rgba(135, 189, 207, 0.1)',
                borderRadius: '12px',
                padding: '15px',
                border: '2px solid var(--mudiko-cyan)'
              }}>
                <h4 style={{ color: 'var(--mudiko-cyan)', margin: '0 0 10px 0', fontSize: '16px' }}>
                  💡 So erhältst du dein Feedback:
                </h4>
                <ol style={{ color: 'var(--font-color)', margin: '0', paddingLeft: '20px', fontSize: '14px' }}>
                  <li style={{ marginBottom: '8px' }}>Drücke auf "Prompt Kopieren", um den Anweisungstext in der Zwischenablage zu speichern</li>
                  <li style={{ marginBottom: '8px' }}>Drücke auf "Analyse-Daten herunterladen", um die Audio-Analysedaten als Textdatei zu speichern</li>
                  <li style={{ marginBottom: '8px' }}>Öffne eine KI deiner Wahl (z.B. Telli, ChatGPT, Claude, Gemini)</li>
                  <li style={{ marginBottom: '8px' }}>Füge den kopierten Prompt in einen neuen Chat ein. Alternativ kannst du auch selbst einen Prompt verfassen</li>
                  <li style={{ marginBottom: '8px' }}>Lade die Audio-Analyse-Daten als Anhang in den Chat hoch</li>
                  <li style={{ marginBottom: '8px' }}>Erhalte dein personalisiertes Musik-Feedback! 🎵</li>
                </ol>
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0' }}>
                Lade deine Daten...
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Navigation am unteren Ende der Seite */}
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', padding: '20px 0', flexShrink: 0 }}>
        <button 
          onClick={handleNewFeedback}
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
          Neues Feedback
        </button>
      </div>

      {/* Prompt Modal */}
      {showPromptModal && (
        <div style={{
          position: 'fixed',
          top: '0',
          left: '0',
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            backgroundColor: 'var(--card-color)',
            borderRadius: '20px',
            padding: '30px',
            width: '90%',
            maxWidth: '800px',
            maxHeight: '80%',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
          }}>
            {/* Modal Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '20px',
              borderBottom: '2px solid #666666',
              paddingBottom: '15px'
            }}>
              <h3 style={{ 
                color: 'var(--font-color)', 
                margin: '0', 
                fontSize: '20px',
                fontWeight: '600'
              }}>
                Feedback-Prompt
              </h3>
              <button
                onClick={() => setShowPromptModal(false)}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: 'var(--font-color)',
                  fontSize: '24px',
                  cursor: 'pointer',
                  padding: '5px',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                  e.target.style.transform = 'scale(1.1)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.transform = 'scale(1)';
                }}
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div style={{
              backgroundColor: 'var(--button-color)',
              borderRadius: '15px',
              padding: '20px',
              border: '2px solid #666666',
              overflowY: 'auto',
              flexGrow: 1,
              marginBottom: '20px'
            }}>
              <pre style={{
                color: 'var(--font-color)',
                margin: '0',
                whiteSpace: 'pre-wrap',
                fontFamily: "'Nunito', sans-serif",
                fontSize: '14px',
                lineHeight: '1.6'
              }}>
                {generatedPrompt}
              </pre>
            </div>

            {/* Modal Actions */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              gap: '15px',
              flexWrap: 'wrap'
            }}>
              <button 
                id="modal-copy-button"
                onClick={copyToClipboardFromModal}
                style={{ 
                  backgroundColor: 'var(--button-color)',
                  border: '3px solid', 
                  borderImage: 'var(--mudiko-gradient) 1',
                  color: 'var(--font-color)',
                  padding: '12px 25px',
                  borderRadius: '0px',
                  cursor: 'pointer',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: 'var(--button-font-size)',
                  fontWeight: 'var(--button-font-weight)',
                  boxShadow: 'var(--shadow)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
              >
                Kopieren
              </button>
              <button 
                onClick={() => setShowPromptModal(false)}
                style={{ 
                  backgroundColor: 'var(--button-color)',
                  border: '2px solid #666666',
                  color: 'var(--font-color)',
                  padding: '12px 25px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: 'var(--button-font-size)',
                  fontWeight: 'var(--button-font-weight)',
                  boxShadow: 'var(--shadow)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
                onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

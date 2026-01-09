import { useState, useEffect } from 'react'

export default function EasyFeedbackResultPage({ onBack, onHome }) {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPromptModal, setShowPromptModal] = useState(false);

  useEffect(() => {
    try {
      const storedResult = localStorage.getItem('easyFeedbackResult');
      if (storedResult) {
        setResult(JSON.parse(storedResult));
      } else {
        setError('Keine Ergebnisse gefunden. Bitte starte den Prozess neu.');
      }
    } catch (err) {
      setError('Fehler beim Laden der Ergebnisse.');
      console.error('Error loading result:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const copyToClipboard = async () => {
    const button = document.getElementById('copy-button');
    const originalText = button.textContent;
    
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(result.system_prompt);
        
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
        
        return;
      }
    } catch (error) {
      console.log('Clipboard API fehlgeschlagen, versuche Fallback:', error);
    }
    
    // Fallback
    try {
      const textArea = document.createElement('textarea');
      textArea.value = result.system_prompt;
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
      textArea.style.fontSize = '16px';
      
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      textArea.setSelectionRange(0, textArea.value.length);
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (successful) {
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
        
        return;
      }
    } catch (error) {
      console.log('execCommand fehlgeschlagen:', error);
    }
    
    button.textContent = '❌ Kopieren nicht möglich';
    button.style.backgroundColor = '#ff6b6b';
    button.style.border = '3px solid #ff6b6b';
    button.style.borderImage = 'none';
    
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
      await navigator.clipboard.writeText(result.system_prompt);
      
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
      const textArea = document.createElement('textarea');
      textArea.value = result.system_prompt;
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

  const downloadAnalysisData = () => {
    if (!result || !result.user_prompt) return;

    const textData = result.user_prompt;
    const blob = new Blob([textData], { type: 'text/plain; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    link.download = `MIDI-Vergleich_${timestamp}.txt`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleNewFeedback = () => {
    localStorage.removeItem('easyFeedbackResult');
    localStorage.removeItem('easyFeedbackSessionId');
    localStorage.removeItem('easyFeedbackSettings');
    if (onHome) {
      onHome();
    } else {
      window.location.href = '/';
    }
  };

  return (
    <div style={{ 
      height: '100vh',
      height: '100dvh',
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
        {/* Header */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback Prompt</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        {/* Content */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px', marginBottom: '20px' }}>
          {isLoading ? (
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
                🎵 Lade Ergebnisse...
              </h3>
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
                ⚠️ Fehler beim Laden
              </h3>
              <p style={{ color: '#ff6b6b', margin: '0', fontWeight: '500' }}>
                {error}
              </p>
            </div>
          ) : result ? (
            <>
              <div style={{ marginBottom: '25px' }}>
                <h3 style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '20px' }}>
                  🎉 Dein personalisiertes Feedback ist vorbereitet!
                </h3>
              </div>

              {/* Action Buttons */}
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
                  <li style={{ marginBottom: '8px' }}>Drücke auf "Analyse-Daten herunterladen", um die MIDI-Vergleichsdaten als Textdatei zu speichern</li>
                  <li style={{ marginBottom: '8px' }}>Öffne eine KI deiner Wahl (z.B. Telli, ChatGPT, Claude, Gemini)</li>
                  <li style={{ marginBottom: '8px' }}>Füge den kopierten Prompt in einen neuen Chat ein. Alternativ kannst du auch selbst einen Prompt verfassen</li>
                  <li style={{ marginBottom: '8px' }}>Lade die MIDI-Vergleichs-Daten als Anhang in den Chat hoch</li>
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

      {/* Navigation */}
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ color: 'var(--font-color)', margin: '0' }}>📝 Dein Feedback-Prompt</h3>
              <button
                onClick={() => setShowPromptModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--font-color)',
                  fontSize: '24px',
                  cursor: 'pointer',
                  padding: '5px'
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{
              flex: 1,
              overflow: 'auto',
              backgroundColor: 'var(--button-color)',
              borderRadius: '10px',
              padding: '15px',
              marginBottom: '20px'
            }}>
              <pre style={{
                color: 'var(--font-color)',
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                fontFamily: 'monospace',
                fontSize: '14px',
                lineHeight: '1.5'
              }}>
                {result?.system_prompt}
              </pre>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'center', gap: '15px' }}>
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
                📋 Prompt kopieren
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

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

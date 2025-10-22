import { useState, useEffect } from 'react'

export default function PromptPage({ onBack }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState('');
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

      const response = await fetch('/api/generate-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setGeneratedPrompt(result.feedback_prompt);
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
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      
      // Visual feedback
      const button = document.getElementById('copy-button');
      const originalText = button.textContent;
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
    }
  };

  const copyToClipboardFromModal = async () => {
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      
      // Visual feedback for modal button
      const button = document.getElementById('modal-copy-button');
      const originalText = button.textContent;
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
    }
  };

  const handleNewFeedback = () => {
    // Clear all stored data
    localStorage.removeItem('formData');
    localStorage.removeItem('uploadData');
    onBack();
  };
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/Rainbow-Line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback Prompt</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
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
                🎵 Feedback wird generiert...
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
                  🎉 Dein personalisiertes Feedback ist bereit!
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
                  Prompt anzeigen
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
              </div>

              {/* Usage Instructions */}
              <div style={{
                backgroundColor: 'rgba(135, 189, 207, 0.1)',
                borderRadius: '12px',
                padding: '15px',
                border: '2px solid var(--mudiko-cyan)'
              }}>
                <h4 style={{ color: 'var(--mudiko-cyan)', margin: '0 0 10px 0', fontSize: '16px' }}>
                  💡 So verwendest du den Prompt:
                </h4>
                <ol style={{ color: 'var(--font-color)', margin: '0', paddingLeft: '20px', fontSize: '14px' }}>
                  <li style={{ marginBottom: '8px' }}>Drücke auf "Prompt Kopieren", um ihn in der Zwischenablage zu speichern</li>
                  <li style={{ marginBottom: '8px' }}>Öffne eine KI deiner Wahl (z.B. Telli, ChatGPT, Claude, Gemini) und füge den Prompt in einen neuen Chat ein</li>
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
      
      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', marginBottom: '20px' }}>
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
                📋 Feedback-Prompt
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
                📋 Kopieren
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

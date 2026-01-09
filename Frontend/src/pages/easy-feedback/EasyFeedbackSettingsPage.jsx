import { useState, useEffect } from 'react'

export default function EasyFeedbackSettingsPage({ onBack, onNext }) {
  const [selectedLanguage, setSelectedLanguage] = useState('Deutsch');
  const [simpleLanguage, setSimpleLanguage] = useState(false);
  const [customLanguage, setCustomLanguage] = useState('');
  const [personalMessage, setPersonalMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [error, setError] = useState(null);
  
  const [availableLanguages, setAvailableLanguages] = useState([
    { value: 'deutsch', label: 'Deutsch (Deutsch)' },
    { value: 'english', label: 'Englisch (English)' },
    { value: 'français', label: 'Französisch (Français)' },
    { value: 'español', label: 'Spanisch (Español)' },
    { value: 'italiano', label: 'Italienisch (Italiano)' },
    { value: 'türkçe', label: 'Türkisch (Türkçe)' },
    { value: 'custom', label: 'Andere Sprache' }
  ]);

  // Load saved settings
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('easyFeedbackSettings');
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        if (settings.language) setSelectedLanguage(settings.language);
        if (settings.simpleLanguage !== undefined) setSimpleLanguage(settings.simpleLanguage);
        if (settings.personalMessage) setPersonalMessage(settings.personalMessage);
      }
    } catch (err) {
      console.error('Error loading settings:', err);
    }
  }, []);

  const handleConfirmCustomLanguage = () => {
    if (customLanguage.trim()) {
      const newLanguage = { value: customLanguage.trim(), label: customLanguage.trim() };
      setAvailableLanguages(prev => [...prev.filter(lang => lang.value !== 'custom'), newLanguage, { value: 'custom', label: 'Andere Sprache' }]);
      setSelectedLanguage(customLanguage.trim());
      setCustomLanguage('');
    }
  };

  const handleGenerateFeedback = async () => {
    setIsProcessing(true);
    setError(null);
    
    const sessionId = localStorage.getItem('easyFeedbackSessionId');
    if (!sessionId) {
      setError('Keine Session gefunden. Bitte starte den Prozess neu.');
      setIsProcessing(false);
      return;
    }

    try {
      // Save settings
      localStorage.setItem('easyFeedbackSettings', JSON.stringify({
        language: selectedLanguage,
        simpleLanguage,
        personalMessage
      }));

      // Step 1: Convert audio to MIDI if needed
      setProcessingStep('Audio wird zu MIDI konvertiert...');
      const convertResponse = await fetch('/api/tools/easy-feedback/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({})
      });
      const convertResult = await convertResponse.json();
      
      if (!convertResult.success) {
        throw new Error(convertResult.error || 'Konvertierung fehlgeschlagen');
      }

      // Step 2: Compare MIDI files
      setProcessingStep('MIDI-Dateien werden verglichen...');
      const compareResponse = await fetch('/api/tools/easy-feedback/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({})
      });
      const compareResult = await compareResponse.json();
      
      if (!compareResult.success) {
        throw new Error(compareResult.error || 'Vergleich fehlgeschlagen');
      }

      // Step 3: Generate prompt
      setProcessingStep('Feedback-Prompt wird generiert...');
      const generateResponse = await fetch('/api/tools/easy-feedback/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({
          language: selectedLanguage,
          personalization: personalMessage,
          simpleLanguage: simpleLanguage
        })
      });
      const generateResult = await generateResponse.json();
      
      if (!generateResult.success) {
        throw new Error(generateResult.error || 'Prompt-Generierung fehlgeschlagen');
      }

      // Store results
      localStorage.setItem('easyFeedbackResult', JSON.stringify(generateResult));

      // Navigate to result page
      if (onNext) onNext();

    } catch (err) {
      console.error('Processing error:', err);
      setError(err.message || 'Ein Fehler ist aufgetreten');
    } finally {
      setIsProcessing(false);
      setProcessingStep('');
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Einstellungen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>

        {/* Content Card */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          {isProcessing ? (
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
                🎵 {processingStep}
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0', opacity: 0.8 }}>
                Bitte warte einen Moment...
              </p>
            </div>
          ) : (
            <>
              <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
                Stelle ein, in welcher Sprache du dein Feedback erhalten möchtest und personalisiere es optional.
              </p>

              {/* Language Selection */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Sprache</span>
                <select 
                  value={selectedLanguage} 
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  style={{ 
                    backgroundColor: 'var(--button-color)', 
                    color: 'var(--font-color)', 
                    border: 'none', 
                    borderRadius: '5px', 
                    padding: '5px 10px',
                    fontFamily: "'Nunito', sans-serif"
                  }}
                >
                  {availableLanguages.map(lang => (
                    <option key={lang.value} value={lang.value}>{lang.label}</option>
                  ))}
                </select>
              </div>

              {selectedLanguage === 'custom' && (
                <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Sprache eingeben"
                    value={customLanguage}
                    onChange={(e) => setCustomLanguage(e.target.value)}
                    style={{
                      flex: 1,
                      padding: '10px',
                      backgroundColor: 'var(--button-color)',
                      color: 'var(--font-color)',
                      border: 'none',
                      borderRadius: '5px',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: '16px'
                    }}
                  />
                  <button
                    onClick={handleConfirmCustomLanguage}
                    disabled={!customLanguage.trim()}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: 'var(--button-color)',
                      color: 'var(--font-color)',
                      border: '2px solid #666666',
                      borderRadius: '10px',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: 'var(--button-font-size)',
                      fontWeight: 'var(--button-font-weight)',
                      cursor: customLanguage.trim() ? 'pointer' : 'not-allowed',
                      opacity: customLanguage.trim() ? 1 : 0.5
                    }}
                  >
                    bestätigen
                  </button>
                </div>
              )}

              {/* Simple Language Toggle */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Einfache Sprache</span>
                <label style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                  <input 
                    type="checkbox" 
                    checked={simpleLanguage} 
                    onChange={(e) => setSimpleLanguage(e.target.checked)}
                    style={{ opacity: 0, width: 0, height: 0 }}
                  />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: simpleLanguage ? 'var(--mudiko-pink)' : 'var(--button-color)',
                    transition: '.4s',
                    borderRadius: '24px'
                  }}>
                    <span style={{
                      position: 'absolute',
                      content: '""',
                      height: '18px',
                      width: '18px',
                      left: simpleLanguage ? '26px' : '3px',
                      bottom: '3px',
                      backgroundColor: 'white',
                      transition: '.4s',
                      borderRadius: '50%'
                    }}></span>
                  </span>
                </label>
              </div>
              
              <p style={{ color: 'var(--font-color)', fontSize: '14px', opacity: 0.7, margin: '0 0 25px 0' }}>
                Wenn aktiviert, wird das Feedback in einfacher und leicht verständlicher Sprache formuliert.
              </p>

              {/* Personalization */}
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', fontWeight: '600' }}>
                Feedback personalisieren (optional)
              </p>
              <textarea
                value={personalMessage}
                onChange={(e) => setPersonalMessage(e.target.value)}
                placeholder='Beispiel: "Hey MuDiKo, ich würde gerne mein Rhythmus-Gefühl verbessern. Lege darauf bitte einen besonderen Fokus."'
                style={{
                  width: '100%',
                  height: '100px',
                  padding: '10px',
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '5px',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: '16px',
                  resize: 'none',
                  marginBottom: '20px',
                  boxSizing: 'border-box'
                }}
              />

              {/* Error Message */}
              {error && (
                <div style={{ 
                  padding: '15px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(255, 107, 107, 0.1)',
                  border: '2px solid #ff6b6b',
                  marginBottom: '20px'
                }}>
                  <p style={{ color: '#ff6b6b', margin: '0', textAlign: 'center' }}>
                    ⚠️ {error}
                  </p>
                </div>
              )}

              {/* Generate Button */}
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <button 
                  onClick={handleGenerateFeedback}
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
                  Feedback generieren
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Spacing */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', marginBottom: '20px' }}>
        <button 
          onClick={onBack}
          disabled={isProcessing}
          style={{
            backgroundColor: 'var(--button-color)',
            color: 'var(--font-color)',
            border: '2px solid #666666',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease',
            opacity: isProcessing ? 0.5 : 1
          }}
          onMouseEnter={(e) => { if (!isProcessing) e.target.style.transform = 'scale(1.02)' }}
          onMouseLeave={(e) => { if (!isProcessing) e.target.style.transform = 'scale(1)' }}
        >
          ← Zurück
        </button>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

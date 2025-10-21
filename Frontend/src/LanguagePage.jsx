import React, { useState, useEffect } from 'react';

export default function LanguagePage({ onBack, onNext }) {
  const [selectedLanguage, setSelectedLanguage] = useState('Deutsch');
  const [simpleLanguage, setSimpleLanguage] = useState(false);
  const [customLanguage, setCustomLanguage] = useState('');
  const [availableLanguages, setAvailableLanguages] = useState([
    { value: 'deutsch', label: 'Deutsch (Deutsch)' },
    { value: 'english', label: 'Englisch (English)' },
    { value: 'français', label: 'Französisch (Français)' },
    { value: 'español', label: 'Spanisch (Español)' },
    { value: 'italiano', label: 'Italienisch (Italiano)' },
    { value: 'türkçe', label: 'Türkisch (Türkçe)' },
    { value: 'custom', label: 'Andere Sprache' }
  ]);

  // Load saved data on component mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem('formData');
      if (savedData) {
        const data = JSON.parse(savedData);
        if (data.language) setSelectedLanguage(data.language);
        if (data.simpleLanguage !== undefined) setSimpleLanguage(data.simpleLanguage);
        if (data.customLanguage) setCustomLanguage(data.customLanguage);
      }
    } catch (error) {
      console.error('Error loading saved language data:', error);
    }
  }, []);

  const handleNext = () => {
    // Save current form data to localStorage
    try {
      const existingData = JSON.parse(localStorage.getItem('formData') || '{}');
      const updatedData = {
        ...existingData,
        language: selectedLanguage,
        customLanguage: selectedLanguage === 'custom' ? customLanguage : '',
        simpleLanguage: simpleLanguage
      };
      localStorage.setItem('formData', JSON.stringify(updatedData));
      onNext();
    } catch (error) {
      console.error('Error saving language data:', error);
      onNext(); // Continue anyway
    }
  };

  const handleConfirmCustomLanguage = () => {
    if (customLanguage.trim()) {
      const newLanguage = { value: customLanguage.trim(), label: customLanguage.trim() };
      setAvailableLanguages(prev => [...prev.filter(lang => lang.value !== 'custom'), newLanguage, { value: 'custom', label: 'Andere Sprache' }]);
      setSelectedLanguage(customLanguage.trim());
      setCustomLanguage('');
    }
  };

  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Sprache einstellen</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>Du kannst nun einstellen, in welcher Sprache du dein Feedback erhalten möchtest. Außerdem kannst du einfache Sprache aktivieren.</p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '30px' }}>
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
            <div style={{ marginBottom: '30px', display: 'flex', gap: '10px', alignItems: 'center' }}>
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
                  padding: '10px 15px',
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '5px',
                  fontFamily: "'Nunito', sans-serif",
                  cursor: customLanguage.trim() ? 'pointer' : 'not-allowed',
                  opacity: customLanguage.trim() ? 1 : 0.5
                }}
              >
                bestätigen
              </button>
            </div>
          )}
          
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
          
          <p style={{ color: 'var(--font-color)', fontSize: '14px', opacity: 0.7, margin: '0' }}>
            Wenn aktiviert, wird das Feedback in einfacher und leicht verständlicher Sprache formuliert. Dies ist z.B. hilfreich für Menschen mit Sprachbarrieren, Leseschwächen oder wenn die bevorzugte Sprache nicht die Muttersprache ist.
          </p>
        </div>
      </div>
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
            fontSize: '16px',
            fontWeight: '600',
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
            border: '2px solid', 
            borderImage: 'var(--mudiko-gradient) 1',
            color: 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: '16px',
            fontWeight: '600',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease'
          }} 
          onClick={handleNext}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          Weiter →
        </button>
      </div>
    </div>
  )
}
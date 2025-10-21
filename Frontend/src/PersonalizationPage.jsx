import React, { useState, useEffect } from 'react';

export default function PersonalizationPage({ onBack, onNext }) {
  const [personalMessage, setPersonalMessage] = useState('');

  // Load saved data on component mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem('formData');
      if (savedData) {
        const data = JSON.parse(savedData);
        if (data.personalMessage) setPersonalMessage(data.personalMessage);
      }
    } catch (error) {
      console.error('Error loading saved personalization data:', error);
    }
  }, []);

  const handleNext = () => {
    // Save current form data to localStorage
    try {
      const existingData = JSON.parse(localStorage.getItem('formData') || '{}');
      const updatedData = {
        ...existingData,
        personalMessage: personalMessage.trim()
      };
      localStorage.setItem('formData', JSON.stringify(updatedData));
      onNext();
    } catch (error) {
      console.error('Error saving personalization data:', error);
      onNext(); // Continue anyway
    }
  };
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback personalisieren</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 15px 0' }}>
            Jetzt hast du die Möglichkeit, dein Feedback noch persönlicher zu gestalten.Du kannst beispielsweise sagen, worauf sie beim Feedback einen besonderen Fokus legen soll oder wo du noch Schwierigkeiten hast.
          </p>
          
          
          <textarea
            value={personalMessage}
            onChange={(e) => setPersonalMessage(e.target.value)}
            placeholder='Beispiel: "Hey MuDiKo, ich würde gerne mein Rhythmus-Gefühl verbessern. Lege darauf bitte einen besonderen Fokus."'
            style={{
              width: '100%',
              height: '120px',
              maxHeight: '200px',
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
          
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button 
              onClick={handleNext}
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
        </div>
      </div>
      
      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', marginBottom: '20px' }}>
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
      </div>
    </div>
  )
}
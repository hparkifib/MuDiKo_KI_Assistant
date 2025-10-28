import React, { useState, useEffect } from 'react';

export default function InstrumentsPage({ onBack, onNext }) {
  const [referenceInstrument, setReferenceInstrument] = useState('');
  const [userInstrument, setUserInstrument] = useState('');

  // Load saved data on component mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem('formData');
      if (savedData) {
        const data = JSON.parse(savedData);
        if (data.referenceInstrument) setReferenceInstrument(data.referenceInstrument);
        if (data.userInstrument) setUserInstrument(data.userInstrument);
      }
    } catch (error) {
      console.error('Error loading saved instrument data:', error);
    }
  }, []);

  const handleNext = () => {
    // Save current form data to localStorage
    try {
      const existingData = JSON.parse(localStorage.getItem('formData') || '{}');
      const updatedData = {
        ...existingData,
        referenceInstrument: referenceInstrument.trim() || 'keine Angabe',
        userInstrument: userInstrument.trim() || 'keine Angabe'
      };
      localStorage.setItem('formData', JSON.stringify(updatedData));
      onNext();
    } catch (error) {
      console.error('Error saving instrument data:', error);
      onNext(); // Continue anyway
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
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Instrumente einstellen</h1>
          <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
            Es hilft der Künstlichen Intelligenz zu wissen, mit welchem Instrument deine Lehrkraft und du eure Audio-Aufnahme eingespielt habt. Gib daher bitte die verwendeten Instrumente an:
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div>
              <label style={{ color: 'var(--font-color)', fontSize: '16px', display: 'block', marginBottom: '5px' }}>
                Instrument Referenz:
              </label>
              <input
                type="text"
                value={referenceInstrument}
                onChange={(e) => setReferenceInstrument(e.target.value)}
                placeholder="z.B. Klavier, Gitarre, Violine..."
                style={{
                  width: '50%',
                  padding: '5px 8px',
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '5px',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div>
              <label style={{ color: 'var(--font-color)', fontSize: '16px', display: 'block', marginBottom: '5px' }}>
                Dein Instrument:
              </label>
              <input
                type="text"
                value={userInstrument}
                onChange={(e) => setUserInstrument(e.target.value)}
                placeholder="z.B. Klavier, Gitarre, Violine..."
                style={{
                  width: '50%',
                  padding: '5px 8px',
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '5px',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: '14px'
                }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Spacing zwischen Content und Navigation */}
      <div style={{ height: 'var(--navigation-spacing)' }}></div>
      
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
          style={{ 
            backgroundColor: 'var(--button-color)',
            border: '2px solid #666666', 
            color: 'var(--font-color)',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
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

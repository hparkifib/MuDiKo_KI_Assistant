import React, { useState, useEffect } from 'react';
import { useToolStorage } from '../../hooks/useToolStorage';

export default function InstrumentsPage({ onBack, onNext, toolType = 'audio' }) {
  const storage = useToolStorage(toolType);
  const [referenceInstrument, setReferenceInstrument] = useState('Klavier');
  const [userInstrument, setUserInstrument] = useState('Klavier');
  const [customReferenceInstrument, setCustomReferenceInstrument] = useState('');
  const [customUserInstrument, setCustomUserInstrument] = useState('');
  const [availableInstruments, setAvailableInstruments] = useState([
    { value: 'Klavier', label: 'Klavier' },
    { value: 'Gitarre', label: 'Gitarre' },
    { value: 'Violine', label: 'Violine' },
    { value: 'Cello', label: 'Cello' },
    { value: 'Kontrabass', label: 'Kontrabass' },
    { value: 'Flöte', label: 'Flöte' },
    { value: 'Klarinette', label: 'Klarinette' },
    { value: 'Saxophon', label: 'Saxophon' },
    { value: 'Trompete', label: 'Trompete' },
    { value: 'Posaune', label: 'Posaune' },
    { value: 'Schlagzeug', label: 'Schlagzeug' },
    { value: 'Gesang', label: 'Gesang' },
    { value: 'custom', label: 'Sonstiges' }
  ]);

  // Load saved data on component mount
  useEffect(() => {
    try {
      const savedData = storage.getItem('formData');
      if (savedData) {
        if (savedData.referenceInstrument) setReferenceInstrument(savedData.referenceInstrument);
        if (savedData.userInstrument) setUserInstrument(savedData.userInstrument);
        if (savedData.customReferenceInstrument) setCustomReferenceInstrument(savedData.customReferenceInstrument);
        if (savedData.customUserInstrument) setCustomUserInstrument(savedData.customUserInstrument);
      }
    } catch (error) {
      console.error('Error loading saved instrument data:', error);
    }
  }, []);

  const handleNext = () => {
    // Save current form data to storage
    try {
      const existingData = storage.getItem('formData') || {};
      const updatedData = {
        ...existingData,
        referenceInstrument: referenceInstrument === 'custom' ? customReferenceInstrument : referenceInstrument,
        userInstrument: userInstrument === 'custom' ? customUserInstrument : userInstrument,
        customReferenceInstrument: referenceInstrument === 'custom' ? customReferenceInstrument : '',
        customUserInstrument: userInstrument === 'custom' ? customUserInstrument : ''
      };
      storage.setItem('formData', updatedData);
      onNext();
    } catch (error) {
      console.error('Error saving instrument data:', error);
      onNext(); // Continue anyway
    }
  };

  const handleConfirmCustomReferenceInstrument = () => {
    if (customReferenceInstrument.trim()) {
      const newInstrument = { value: customReferenceInstrument.trim(), label: customReferenceInstrument.trim() };
      setAvailableInstruments(prev => [...prev.filter(inst => inst.value !== 'custom'), newInstrument, { value: 'custom', label: 'Sonstiges' }]);
      setReferenceInstrument(customReferenceInstrument.trim());
      setCustomReferenceInstrument('');
    }
  };

  const handleConfirmCustomUserInstrument = () => {
    if (customUserInstrument.trim()) {
      const newInstrument = { value: customUserInstrument.trim(), label: customUserInstrument.trim() };
      setAvailableInstruments(prev => [...prev.filter(inst => inst.value !== 'custom'), newInstrument, { value: 'custom', label: 'Sonstiges' }]);
      setUserInstrument(customUserInstrument.trim());
      setCustomUserInstrument('');
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
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
            {/* Referenz-Instrument */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Instrument Referenz</span>
                <select 
                  value={referenceInstrument} 
                  onChange={(e) => setReferenceInstrument(e.target.value)}
                  style={{ 
                    backgroundColor: 'var(--button-color)', 
                    color: 'var(--font-color)', 
                    border: 'none', 
                    borderRadius: '5px', 
                    padding: '5px 10px',
                    fontFamily: "'Nunito', sans-serif"
                  }}
                >
                  {availableInstruments.map(inst => (
                    <option key={inst.value} value={inst.value}>{inst.label}</option>
                  ))}
                </select>
              </div>
              
              {referenceInstrument === 'custom' && (
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Instrument eingeben"
                    value={customReferenceInstrument}
                    onChange={(e) => setCustomReferenceInstrument(e.target.value)}
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
                    onClick={handleConfirmCustomReferenceInstrument}
                    disabled={!customReferenceInstrument.trim()}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: 'var(--button-color)',
                      color: 'var(--font-color)',
                      border: '2px solid #666666',
                      borderRadius: '10px',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: 'var(--button-font-size)',
                      fontWeight: 'var(--button-font-weight)',
                      cursor: customReferenceInstrument.trim() ? 'pointer' : 'not-allowed',
                      opacity: customReferenceInstrument.trim() ? 1 : 0.5,
                      boxShadow: customReferenceInstrument.trim() ? 'var(--shadow)' : 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (customReferenceInstrument.trim()) {
                        e.target.style.transform = 'scale(1.02)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (customReferenceInstrument.trim()) {
                        e.target.style.transform = 'scale(1)';
                      }
                    }}
                  >
                    bestätigen
                  </button>
                </div>
              )}
            </div>

            {/* Benutzer-Instrument */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Dein Instrument</span>
                <select 
                  value={userInstrument} 
                  onChange={(e) => setUserInstrument(e.target.value)}
                  style={{ 
                    backgroundColor: 'var(--button-color)', 
                    color: 'var(--font-color)', 
                    border: 'none', 
                    borderRadius: '5px', 
                    padding: '5px 10px',
                    fontFamily: "'Nunito', sans-serif"
                  }}
                >
                  {availableInstruments.map(inst => (
                    <option key={inst.value} value={inst.value}>{inst.label}</option>
                  ))}
                </select>
              </div>
              
              {userInstrument === 'custom' && (
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Instrument eingeben"
                    value={customUserInstrument}
                    onChange={(e) => setCustomUserInstrument(e.target.value)}
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
                    onClick={handleConfirmCustomUserInstrument}
                    disabled={!customUserInstrument.trim()}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: 'var(--button-color)',
                      color: 'var(--font-color)',
                      border: '2px solid #666666',
                      borderRadius: '10px',
                      fontFamily: "'Nunito', sans-serif",
                      fontSize: 'var(--button-font-size)',
                      fontWeight: 'var(--button-font-weight)',
                      cursor: customUserInstrument.trim() ? 'pointer' : 'not-allowed',
                      opacity: customUserInstrument.trim() ? 1 : 0.5,
                      boxShadow: customUserInstrument.trim() ? 'var(--shadow)' : 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (customUserInstrument.trim()) {
                        e.target.style.transform = 'scale(1.02)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (customUserInstrument.trim()) {
                        e.target.style.transform = 'scale(1)';
                      }
                    }}
                  >
                    bestätigen
                  </button>
                </div>
              )}
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

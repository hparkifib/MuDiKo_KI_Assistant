import React, { useState } from 'react';

export default function InstrumentsPage({ onBack, onNext }) {
  const [referenceInstrument, setReferenceInstrument] = useState('');
  const [userInstrument, setUserInstrument] = useState('');
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Instrumente einstellen</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
            Es hilft der Künstlichen Intelligenz zu wissen, mit welchem Instrument deine Lehrkraft und du eure Audio-Aufnahme eingespeilt habt. Gib daher bitte die verwendeten Instrumente an:
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
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '95%', marginBottom: '20px' }}>
        <button onClick={onBack}>zurück</button>
        <button style={{ border: '2px solid', borderImage: 'var(--mudiko-gradient) 1' }} onClick={onNext}>weiter</button>
      </div>
    </div>
  )
}
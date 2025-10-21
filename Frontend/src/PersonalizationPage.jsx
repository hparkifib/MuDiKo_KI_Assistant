import React, { useState } from 'react';

export default function PersonalizationPage({ onBack, onNext }) {
  const [personalMessage, setPersonalMessage] = useState('');
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback personalisieren</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 15px 0' }}>
            Jetzt hast du die Möglichkeit, dein Feedback noch persönlicher zu gestalten.
          </p>
          <p style={{ color: 'var(--font-color)', margin: '0 0 25px 0' }}>
            Du kannst beispielsweise sagen, worauf sie beim Feedback einen besonderen Fokus legen soll oder wo du noch Schwierigkeiten hast.
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
            <button onClick={onNext} style={{ border: '2px solid', borderImage: 'var(--mudiko-gradient) 1' }}>Feedback generieren</button>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', marginBottom: '20px' }}>
        <button onClick={onBack}>zurück</button>
      </div>
    </div>
  )
}
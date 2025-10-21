import React, { useState, useEffect } from 'react';

export default function PersonalizationPage({ onBack, onNext }) {
  const [topics, setTopics] = useState([]);
  const [personalMessage, setPersonalMessage] = useState('');

  // Available feedback topics
  const availableTopics = [
    'Tempo', 'Rhythmus', 'Tonalität', 'Dynamik', 
    'Klangfarbe', 'Intonation', 'Phrasierung', 'Artikulation'
  ];

  // Load saved data on component mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem('formData');
      if (savedData) {
        const data = JSON.parse(savedData);
        if (data.topics) setTopics(data.topics);
        if (data.personalMessage) setPersonalMessage(data.personalMessage);
      }
    } catch (error) {
      console.error('Error loading saved personalization data:', error);
    }
  }, []);

  const handleTopicToggle = (topic) => {
    setTopics(prev => 
      prev.includes(topic) 
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const handleNext = () => {
    // Save current form data to localStorage
    try {
      const existingData = JSON.parse(localStorage.getItem('formData') || '{}');
      const updatedData = {
        ...existingData,
        topics: topics,
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
            Jetzt hast du die Möglichkeit, dein Feedback noch persönlicher zu gestalten.
          </p>
          <p style={{ color: 'var(--font-color)', margin: '0 0 25px 0' }}>
            Wähle aus, worauf das Feedback besonders eingehen soll:
          </p>

          {/* Feedback Topics Selection */}
          <div style={{ marginBottom: '25px' }}>
            <h3 style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '18px' }}>
              Schwerpunkt im Feedback:
            </h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '10px'
            }}>
              {availableTopics.map(topic => (
                <label 
                  key={topic}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '10px',
                    backgroundColor: topics.includes(topic) ? 'rgba(135, 189, 207, 0.2)' : 'var(--button-color)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    border: topics.includes(topic) ? '2px solid var(--mudiko-cyan)' : '2px solid transparent',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (!topics.includes(topic)) {
                      e.target.style.backgroundColor = 'rgba(87, 87, 87, 0.8)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!topics.includes(topic)) {
                      e.target.style.backgroundColor = 'var(--button-color)';
                    }
                  }}
                >
                  <input
                    type="checkbox"
                    checked={topics.includes(topic)}
                    onChange={() => handleTopicToggle(topic)}
                    style={{ marginRight: '8px', accentColor: 'var(--mudiko-cyan)' }}
                  />
                  <span style={{ color: 'var(--font-color)', fontSize: '14px', fontWeight: '500' }}>
                    {topic}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Personal Message */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ color: 'var(--font-color)', margin: '0 0 10px 0', fontSize: '18px' }}>
              Persönliche Nachricht (optional):
            </h3>
            <p style={{ color: 'var(--font-color)', margin: '0 0 15px 0', fontSize: '14px', opacity: 0.8 }}>
              Du kannst zusätzlich eine persönliche Nachricht hinzufügen, z.B. worauf du besonderen Fokus legen möchtest.
            </p>
          </div>
          
          <textarea
            value={personalMessage}
            onChange={(e) => setPersonalMessage(e.target.value)}
            placeholder='Beispiel: "Hey MuDiKo, ich würde gerne mein Rhythmus-Gefühl verbessern. Lege darauf bitte einen besonderen Fokus."'
            style={{
              width: '100%',
              height: '120px',
              maxHeight: '200px',
              padding: '15px',
              backgroundColor: 'var(--button-color)',
              color: 'var(--font-color)',
              border: 'none',
              borderRadius: '10px',
              fontFamily: "'Nunito', sans-serif",
              fontSize: '16px',
              resize: 'vertical',
              marginBottom: '25px',
              boxSizing: 'border-box',
              outline: 'none'
            }}
          />
          
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button 
              onClick={handleNext}
              style={{ 
                backgroundColor: 'var(--button-color)',
                border: '2px solid', 
                borderImage: 'var(--mudiko-gradient) 1',
                color: 'var(--font-color)',
                padding: '15px 30px',
                borderRadius: '10px',
                cursor: 'pointer',
                fontFamily: "'Nunito', sans-serif",
                fontSize: '18px',
                fontWeight: '600',
                boxShadow: 'var(--shadow)',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              🎵 Feedback generieren
            </button>
          </div>
        </div>
      </div>
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
      </div>
    </div>
  )
}
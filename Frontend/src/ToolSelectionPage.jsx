// Tool Selection Page - Wähle zwischen Audio und MIDI Tool

export default function ToolSelectionPage({ onSelectAudio, onSelectMidi, onBack }) {
  return (
    <div
      style={{
        minHeight: '100vh', /* Fallback */
        minHeight: '100dvh', /* Dynamic viewport height */
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
        alignItems: 'center',
        padding: '0',
        position: 'relative',
        overflow: 'hidden',
        boxSizing: 'border-box'
      }}
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', width: '100%' }}>
        <h1 style={{
          textAlign: 'center',
          color: 'var(--font-color)',
          marginBottom: '20px',
          fontSize: '22px',
          zIndex: 1
        }}>
          Welches Dateiformat möchtest du analysieren?
        </h1>

        <div style={{
          display: 'flex',
          gap: '20px',
          justifyContent: 'center',
          alignItems: 'stretch',
          flexWrap: 'wrap',
          width: '90%',
          maxWidth: '900px',
          zIndex: 1,
          boxSizing: 'border-box'
        }}>
        {/* Audio Feedback Tool */}
        <div
          style={{
            backgroundColor: 'var(--card-color)',
            borderRadius: '20px',
            padding: '20px',
            width: '100%',
            maxWidth: '320px',
            boxShadow: 'var(--shadow)',
            cursor: 'pointer',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            border: '2px solid transparent',
            boxSizing: 'border-box'
          }}
          onClick={onSelectAudio}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)';
            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            e.currentTarget.style.border = '2px solid var(--primary-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'var(--shadow)';
            e.currentTarget.style.border = '2px solid transparent';
          }}
        >
          <div style={{
            fontSize: '40px',
            textAlign: 'center',
            marginBottom: '12px'
          }}>
            🎵
          </div>
          <h2 style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            marginBottom: '10px',
            fontSize: '20px'
          }}>
            MP3-Analyse
          </h2>
          <p style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            opacity: 0.8,
            lineHeight: '1.4',
            fontSize: '14px'
          }}>
            Vergleiche eine Referenzaufnahme mit der Schüleraufnahme und erhalte detailliertes Feedback.
          </p>
          <div style={{
            marginTop: '12px',
            padding: '6px',
            backgroundColor: 'rgba(128, 128, 128, 0.1)',
            borderRadius: '8px',
            fontSize: '13px',
            color: 'var(--font-color)',
            opacity: 0.7,
            textAlign: 'center'
          }}>
            MP3, WAV, MP4
          </div>
        </div>

        {/* MIDI Comparison Tool */}
        <div
          style={{
            backgroundColor: 'var(--card-color)',
            borderRadius: '20px',
            padding: '20px',
            width: '100%',
            maxWidth: '320px',
            boxShadow: 'var(--shadow)',
            cursor: 'pointer',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            border: '2px solid transparent',
            boxSizing: 'border-box'
          }}
          onClick={onSelectMidi}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)';
            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            e.currentTarget.style.border = '2px solid var(--primary-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'var(--shadow)';
            e.currentTarget.style.border = '2px solid transparent';
          }}
        >
          <div style={{
            fontSize: '40px',
            textAlign: 'center',
            marginBottom: '12px'
          }}>
            🎹
          </div>
          <h2 style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            marginBottom: '10px',
            fontSize: '20px'
          }}>
            MIDI-Analyse
          </h2>
          <p style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            opacity: 0.8,
            lineHeight: '1.4',
            fontSize: '14px'
          }}>
            Vergleiche eine Referenz-MIDI mit der Schüler-MIDI und erhalte detailliertes Feedback.
          </p>
          <div style={{
            marginTop: '12px',
            padding: '6px',
            backgroundColor: 'rgba(128, 128, 128, 0.1)',
            borderRadius: '8px',
            fontSize: '13px',
            color: 'var(--font-color)',
            opacity: 0.7,
            textAlign: 'center'
          }}>
            MID, MIDI
          </div>
        </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div style={{ width: '90%', display: 'flex', justifyContent: 'flex-start', marginBottom: '20px', zIndex: 1 }}>
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
  );
}

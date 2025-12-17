// Tool Selection Page - Wähle zwischen Audio und MIDI Tool
import { PageLayout, Card } from '../../components/common';

export default function ToolSelectionPage({ onSelectAudio, onSelectMidi, onSelectMp3ToMidi, onBack }) {
  const toolCardStyle = {
    width: '280px',
    minWidth: '280px',
    flexShrink: 0,
    cursor: 'pointer',
    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
    border: '2px solid transparent',
    boxSizing: 'border-box'
  };

  const handleCardHover = (e, isHovering) => {
    if (isHovering) {
      e.currentTarget.style.transform = 'translateY(-5px)';
      e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
      e.currentTarget.style.border = '2px solid var(--primary-color)';
    } else {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'var(--shadow)';
      e.currentTarget.style.border = '2px solid transparent';
    }
  };

  return (
    <PageLayout>
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
          flexWrap: 'nowrap',
          width: '90%',
          overflowX: 'auto',
          overflowY: 'hidden',
          zIndex: 1,
          boxSizing: 'border-box',
          paddingBottom: '10px'
        }}>
          {/* Audio Feedback Tool */}
          <Card
            style={toolCardStyle}
            onClick={onSelectAudio}
            onMouseEnter={(e) => handleCardHover(e, true)}
            onMouseLeave={(e) => handleCardHover(e, false)}
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
              Audio-Vergleich
            </h2>
            <p style={{
              color: 'var(--font-color)',
              textAlign: 'center',
              opacity: 0.8,
              lineHeight: '1.4',
              fontSize: '14px'
            }}>
              Vergleiche deine Aufnahme mit einer Vorspiel-Aufnahme und lass dir Feedback erstellen.
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
          </Card>

          {/* MIDI Comparison Tool */}
          <Card
            style={toolCardStyle}
            onClick={onSelectMidi}
            onMouseEnter={(e) => handleCardHover(e, true)}
            onMouseLeave={(e) => handleCardHover(e, false)}
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
            MIDI-Vergleich
          </h2>
          <p style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            opacity: 0.8,
            lineHeight: '1.4',
            fontSize: '14px'
          }}>
            Vergleiche deine MIDI-Datei mit einer Vorlage und lass dir Feedback erstellen.
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
        </Card>

        {/* MP3-to-MIDI Converter Tool */}
        <Card
          style={toolCardStyle}
          onClick={onSelectMp3ToMidi}
          onMouseEnter={(e) => handleCardHover(e, true)}
          onMouseLeave={(e) => handleCardHover(e, false)}
        >
          <div style={{
            fontSize: '40px',
            textAlign: 'center',
            marginBottom: '12px'
          }}>
            🎼
          </div>
            <h2 style={{
              color: 'var(--font-color)',
              textAlign: 'center',
              marginBottom: '10px',
              fontSize: '20px'
            }}>
            Audio-zu-MIDI-Umwandlung
          </h2>
          <p style={{
            color: 'var(--font-color)',
            textAlign: 'center',
            opacity: 0.8,
            lineHeight: '1.4',
            fontSize: '14px'
          }}>
            Wandle deine Aufnahme in MIDI-Noten um - optimiert für dein Instrument.
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
            MP3, WAV, MP4 → MIDI
          </div>
        </Card>
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
    </PageLayout>
  );
}

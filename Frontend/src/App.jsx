/**
 * MuDiKo KI Assistant - Haupt-App-Komponente
 * Verwaltet Navigation zwischen Audio-Feedback und MIDI-Comparison Tools
 */
import { useState, useEffect } from 'react'
import ToolSelectionPage from './pages/common/ToolSelectionPage.jsx'
import AudioFeedbackUploadPage from './pages/audio-feedback/AudioFeedbackUploadPage.jsx'
import MidiComparisonUploadPage from './pages/midi-comparison/MidiComparisonUploadPage.jsx'
import Mp3ToMidiUploadPage from './pages/mp3-to-midi-feedback/Mp3ToMidiUploadPage.jsx'
import Mp3ToMidiResultPage from './pages/mp3-to-midi-feedback/Mp3ToMidiResultPage.jsx'
import AudioFeedbackRecordingsPage from './pages/audio-feedback/AudioFeedbackRecordingsPage.jsx'
import CommonLanguagePage from './pages/common/CommonLanguagePage.jsx'
import MidiComparisonLanguagePage from './pages/midi-comparison/MidiComparisonLanguagePage.jsx'
import AudioFeedbackInstrumentsPage from './pages/audio-feedback/AudioFeedbackInstrumentsPage.jsx'
import CommonPersonalizationPage from './pages/common/CommonPersonalizationPage.jsx'
import MidiComparisonPersonalizationPage from './pages/midi-comparison/MidiComparisonPersonalizationPage.jsx'
import CommonPromptPage from './pages/common/CommonPromptPage.jsx'

export default function App() {
  const [page, setPage] = useState('home')

  // Tool Selection Page
  if (page === 'tool-selection') {
    return <ToolSelectionPage 
      onSelectAudio={() => setPage('AudioUpload_Page')} 
      onSelectMidi={() => setPage('midi-upload')}
      onSelectMp3ToMidi={() => setPage('mp3-to-midi-upload')}
      onBack={() => setPage('home')} 
    />
  }

  if (page === 'AudioUpload_Page') {
    return <AudioFeedbackUploadPage onNext={() => setPage('recordings')} />
  }

  // MP3-to-MIDI Flow (Phase 1)
  if (page === 'mp3-to-midi-upload') {
    return <Mp3ToMidiUploadPage onNext={() => setPage('home')} onShowResult={() => setPage('mp3-to-midi-result')} />
  }

  if (page === 'mp3-to-midi-result') {
    return <Mp3ToMidiResultPage onBack={() => setPage('mp3-to-midi-upload')} onHome={() => setPage('home')} />
  }

  // MIDI Flow
  if (page === 'midi-upload') {
    return <MidiComparisonUploadPage onNext={() => setPage('midi-language')} />
  }

  if (page === 'midi-language') {
    return <MidiComparisonLanguagePage onBack={() => setPage('midi-upload')} onNext={() => setPage('midi-personalization')} />
  }

  if (page === 'midi-personalization') {
    return <MidiComparisonPersonalizationPage onBack={() => setPage('midi-language')} onNext={() => setPage('midi-prompt')} />
  }

  if (page === 'midi-prompt') {
    return <CommonPromptPage onBack={() => setPage('home')} toolType="midi" />
  }

  // Audio Flow
  if (page === 'recordings') {
    return <AudioFeedbackRecordingsPage onBack={() => setPage('AudioUpload_Page')} onNext={() => setPage('language')} />
  }

  if (page === 'language') {
    return <CommonLanguagePage onBack={() => setPage('recordings')} onNext={() => setPage('instruments')} />
  }

  if (page === 'instruments') {
    return <AudioFeedbackInstrumentsPage onBack={() => setPage('language')} onNext={() => setPage('personalization')} />
  }

  if (page === 'personalization') {
    return <CommonPersonalizationPage onBack={() => setPage('instruments')} onNext={() => setPage('prompt')} />
  }

  if (page === 'prompt') {
    return <CommonPromptPage onBack={() => setPage('home')} />
  }

  return (
    <div
      id="canvas"
      style={{
        minHeight: '100vh', /* Fallback für ältere Browser */
        minHeight: '100dvh', /* Dynamic Viewport Height - berücksichtigt Toolbar */
        height: '100dvh', /* Feste Höhe für optimale Platznutzung */
        width: '100%',
        backgroundColor: 'var(--bg-color)',
        backgroundImage: 'url(/Rainbow-Line.svg)',
        backgroundPosition: 'bottom 20px center', /* 20px Abstand vom unteren Rand */
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'contain',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
        animation: 'fadeIn 1s ease-in-out'
      }}
    >
      {/* Floating musical notes background */}
      <img 
        src="/noteY.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '5%',
          left: '3%',
          width: '40px',
          height: '40px',
          opacity: 0.3,
          animation: 'floatNote1 8s ease-in-out infinite',
          zIndex: 0
        }}
      />
      <img 
        src="/noteC.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '8%',
          right: '5%',
          width: '35px',
          height: '35px',
          opacity: 0.25,
          animation: 'floatNote2 10s ease-in-out infinite 1s',
          zIndex: 0
        }}
      />
      <img 
        src="/notep.svg" 
        alt="" 
        style={{
          position: 'absolute',
          bottom: '20%', /* Von 15% auf 20% erhöht */
          left: '4%',
          width: '45px',
          height: '45px',
          opacity: 0.2,
          animation: 'floatNote3 12s ease-in-out infinite 2s',
          zIndex: 0
        }}
      />
      <img 
        src="/NoteF.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '12%',
          right: '25%',
          width: '38px',
          height: '38px',
          opacity: 0.35,
          animation: 'floatNote4 9s ease-in-out infinite 0.5s',
          zIndex: 0
        }}
      />
      <img 
        src="/noteY.svg" 
        alt="" 
        style={{
          position: 'absolute',
          bottom: '13%', /* Von 8% auf 13% erhöht */
          right: '3%',
          width: '42px',
          height: '42px',
          opacity: 0.28,
          animation: 'floatNote1 11s ease-in-out infinite 3s',
          zIndex: 0
        }}
      />
      <img 
        src="/noteC.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '25%',
          left: '8%',
          width: '36px',
          height: '36px',
          opacity: 0.22,
          animation: 'floatNote2 13s ease-in-out infinite 1.5s',
          zIndex: 0
        }}
      />
      <img 
        src="/notep.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '18%',
          right: '40%',
          width: '32px',
          height: '32px',
          opacity: 0.4,
          animation: 'floatNote5 7s ease-in-out infinite 4s',
          zIndex: 0
        }}
      />
      <img 
        src="/NoteF.svg" 
        alt="" 
        style={{
          position: 'absolute',
          bottom: '25%', /* Von 20% auf 25% erhöht */
          left: '15%',
          width: '48px',
          height: '48px',
          opacity: 0.18,
          animation: 'floatNote6 15s ease-in-out infinite 2.5s',
          zIndex: 0
        }}
      />
      <img 
        src="/noteY.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '35%',
          right: '8%',
          width: '30px',
          height: '30px',
          opacity: 0.32,
          animation: 'floatNote3 10s ease-in-out infinite 5s',
          zIndex: 0
        }}
      />
      <img 
        src="/noteC.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '45%',
          left: '20%',
          width: '44px',
          height: '44px',
          opacity: 0.26,
          animation: 'floatNote4 12s ease-in-out infinite 3.5s',
          zIndex: 0
        }}
      />
      <img 
        src="/notep.svg" 
        alt="" 
        style={{
          position: 'absolute',
          bottom: '40%', /* Von 35% auf 40% erhöht */
          right: '18%',
          width: '38px',
          height: '38px',
          opacity: 0.3,
          animation: 'floatNote5 9s ease-in-out infinite 1s',
          zIndex: 0
        }}
      />
      <img 
        src="/NoteF.svg" 
        alt="" 
        style={{
          position: 'absolute',
          top: '55%',
          left: '5%',
          width: '34px',
          height: '34px',
          opacity: 0.24,
          animation: 'floatNote6 11s ease-in-out infinite 4.5s',
          zIndex: 0
        }}
      />

      <h1 style={{ 
        textAlign: 'center', 
        color: 'var(--font-color)', 
        marginBottom: '20px', 
        fontSize: '30px',
        position: 'relative',
        zIndex: 1,
        animation: 'slideUp 0.8s ease-out 0.2s both'
      }}>Dein KI-Musik-Assistent</h1>
      <div style={{ 
        backgroundColor: 'var(--card-color)', 
        borderRadius: '30px', 
        padding: '20px', 
        marginBottom: '20px', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        position: 'relative',
        zIndex: 1,
        animation: 'scaleIn 0.6s ease-out 0.4s both'
      }}>
        <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '160px', height: '160px' }} />
      </div>
      <button 
        style={{
          background: 'var(--button-color)',
          border: '3px solid',
          borderImage: 'var(--mudiko-gradient) 1',
          color: 'var(--font-color)',
          padding: '15px 30px',
          borderRadius: '0px',
          boxShadow: 'var(--shadow)',
          fontFamily: "'Nunito', sans-serif",
          fontSize: 'var(--button-font-size)',
          cursor: 'pointer',
          position: 'relative',
          zIndex: 1,
          animation: 'pulse 2s infinite 0.8s',
          transition: 'all 0.3s ease',
        }}
        onClick={() => setPage('tool-selection')}
        onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
      >
        Jetzt Feedback einholen
      </button>
    </div>
  )
}

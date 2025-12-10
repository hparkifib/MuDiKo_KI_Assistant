// Minimal blank canvas App
import { useState, useEffect } from 'react'
import AudioUpload from './AudioUpload_Page.jsx'
import RecordingsPage from './RecordingsPage.jsx'
import LanguagePage from './LanguagePage.jsx'
import InstrumentsPage from './InstrumentsPage.jsx'
import PersonalizationPage from './PersonalizationPage.jsx'
import PromptPage from './PromptPage.jsx'

export default function App() {
  const [page, setPage] = useState('home')

  // Cleanup beim Tab/Browser-Schließen
  useEffect(() => {
    const cleanupSession = () => {
      const sessionId = sessionStorage.getItem('sessionId')
      if (sessionId) {
        // Verwende sendBeacon für zuverlässiges Cleanup beim Schließen
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/tools/audio-feedback/session/cleanup`
        const blob = new Blob([JSON.stringify({ sessionId })], { type: 'application/json' })
        navigator.sendBeacon(url, blob)
      }
    }

    // Registriere Event-Listener
    window.addEventListener('beforeunload', cleanupSession)
    window.addEventListener('pagehide', cleanupSession)

    // Cleanup beim Component unmount
    return () => {
      window.removeEventListener('beforeunload', cleanupSession)
      window.removeEventListener('pagehide', cleanupSession)
    }
  }, [])

  if (page === 'AudioUpload_Page') {
    return <AudioUpload onNext={() => setPage('recordings')} />
  }

  if (page === 'recordings') {
    return <RecordingsPage onBack={() => setPage('AudioUpload_Page')} onNext={() => setPage('language')} />
  }

  if (page === 'language') {
    return <LanguagePage onBack={() => setPage('recordings')} onNext={() => setPage('instruments')} />
  }

  if (page === 'instruments') {
    return <InstrumentsPage onBack={() => setPage('language')} onNext={() => setPage('personalization')} />
  }

  if (page === 'personalization') {
    return <PersonalizationPage onBack={() => setPage('instruments')} onNext={() => setPage('prompt')} />
  }

  if (page === 'prompt') {
    return <PromptPage onBack={() => setPage('home')} />
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
        onClick={() => setPage('AudioUpload_Page')}
        onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
      >
        Jetzt Feedback einholen
      </button>
    </div>
  )
}

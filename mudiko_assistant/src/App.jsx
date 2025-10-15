// Minimal blank canvas App
import { useState } from 'react'
import AudioUpload from './AudioUpload_Page.jsx'
import RecordingsPage from './RecordingsPage.jsx'
import LanguagePage from './LanguagePage.jsx'
import InstrumentsPage from './InstrumentsPage.jsx'
import PersonalizationPage from './PersonalizationPage.jsx'
import PromptPage from './PromptPage.jsx'

export default function App() {
  const [page, setPage] = useState('home')

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
        minHeight: '100vh',
        width: '100%',
        backgroundColor: 'var(--bg-color)',
        backgroundImage: 'url(/src/assets/rainbow-line.svg)',
        backgroundPosition: 'bottom',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'contain',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <h1 style={{ textAlign: 'center', color: 'var(--font-color)', marginBottom: '20px', fontSize: 'var(--title-font-size)' }}>Dein KI-Musik-Assistent</h1>
      <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginBottom: '20px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '150px', height: '150px' }} />
      </div>
      <button 
        style={{
          background: 'var(--button-color)',
          border: '2px solid',
          borderImage: 'var(--mudiko-gradient) 1',
          color: 'var(--font-color)',
          padding: '10px 20px',
          borderRadius: '10px',
          boxShadow: 'var(--shadow)',
          fontFamily: "'Nunito', sans-serif",
          cursor: 'pointer',
        }}
        onClick={() => setPage('AudioUpload_Page')}
      >
        Jetzt Feedback einholen
      </button>
    </div>
  )
}

export default function RecordingsPage({ onBack, onNext }) {
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Deine Aufnahmen</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>Hier können Sie Ihre Aufnahmen verwalten.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Referenz</span>
              <audio controls style={{ height: '30px', backgroundColor: 'var(--button-color)', borderRadius: '5px' }}>
                <source src="/path/to/reference.mp3" type="audio/mpeg" />
                Ihr Browser unterstützt das Audio-Element nicht.
              </audio>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--font-color)', fontSize: '16px' }}>Dein Song</span>
              <audio controls style={{ height: '30px', backgroundColor: 'var(--button-color)', borderRadius: '5px' }}>
                <source src="/path/to/song.mp3" type="audio/mpeg" />
                Ihr Browser unterstützt das Audio-Element nicht.
              </audio>
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
export default function PromptPage({ onBack }) {
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Feedback Prompt</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
            Super! Der MuDiKo-KI-Assistent hat dir einen Prompt erstellt mit dem du dir, von einer KI deiner Wahl, ein individuelles Feedback zu deiner Musik geben lassen kannst.
          </p>
          <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0' }}>
            Probiere es gleich aus. Drücke auf Prompt kopieren, um den Prompt in die Zwischenablage zu speichern. Füge den Prompt anschließend in einen neuen Chat der Telli-KI!
          </p>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button style={{ border: '2px solid', borderImage: 'var(--mudiko-gradient) 1' }}>Prompt kopieren</button>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-start', width: '95%', marginBottom: '20px' }}>
        <button onClick={onBack}>Neues Feedback</button>
      </div>
    </div>
  )
}
// Minimal blank canvas App
import { useState } from 'react'

export default function AudioUpload_Page({ onNext }) {
  const [refFile, setRefFile] = useState('');
  const [songFile, setSongFile] = useState('');
  return (
    <div style={{ minHeight: '100vh', width: '100%', backgroundColor: 'var(--bg-color)', backgroundImage: 'url(/src/assets/rainbow-line.svg)', backgroundPosition: 'top', backgroundRepeat: 'no-repeat', backgroundSize: 'contain', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Aufnahmen hochladen</h1>
          <img src="/src/assets/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
        </div>
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '50px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Referenz</p>
              <label htmlFor="ref-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="ref-upload" accept="audio/mp3,audio/wav,video/mp4" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['audio/mpeg', 'audio/wav', 'video/mp4', 'audio/mp4'].includes(file.type)) {
                  alert('Nicht unterstützter Dateityp. Bitte wählen Sie MP3, WAV oder MP4.');
                  e.target.value = '';
                  setRefFile('');
                  return;
                }
                setRefFile(file?.name || '');
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade die Musik-Datei deiner Lehrkraft hoch!</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach der Musik deiner Lehrkraft. Unterstützte Formate sind: MP3, WAV und MP4</p>
              {refFile && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{refFile}</p>}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '70px' }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0', whiteSpace: 'nowrap' }}>Dein Song</p>
              <label htmlFor="song-upload" style={{ width: '50px', height: '50px', backgroundColor: 'var(--button-color)', border: 'none', borderRadius: '5px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '24px', color: 'var(--font-color)', cursor: 'pointer' }}>+</label>
              <input type="file" id="song-upload" accept="audio/mp3,audio/wav,video/mp4" style={{ display: 'none' }} onChange={(e) => {
                const file = e.target.files[0];
                if (file && !['audio/mpeg', 'audio/wav', 'video/mp4', 'audio/mp4'].includes(file.type)) {
                  alert('Nicht unterstützter Dateityp. Bitte wählen Sie MP3, WAV oder MP4.');
                  e.target.value = '';
                  setSongFile('');
                  return;
                }
                setSongFile(file?.name || '');
              }} />
            </div>
            <div style={{ marginLeft: '20px', flex: 1 }}>
              <p style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>Lade deine Musik hoch</p>
              <p style={{ fontSize: '14px', color: 'var(--font-color)', opacity: 0.7, margin: '0 0 10px 0' }}>Tippe auf das "+" und suche in deinen Dateien nach deiner Musik. Unterstützte Formate sind: MP3, WAV und MP4</p>
              {songFile && <p style={{ color: 'var(--font-color)', fontSize: '14px', margin: '0' }}>{songFile}</p>}
            </div>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', width: '95%', marginBottom: '20px' }}>
        <button style={{ border: '2px solid', borderImage: 'var(--mudiko-gradient) 1' }} onClick={onNext}>Musik hochladen</button>
      </div>
    </div>
  )
}
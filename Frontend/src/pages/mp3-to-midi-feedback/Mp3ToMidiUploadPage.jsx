import GenericUploadPage from '../../components/common/GenericUploadPage'

export default function Mp3ToMidiUploadPage({ onNext, onShowResult }) {
  return (
    <GenericUploadPage
      title="MP3-Dateien hochladen"
      refLabel="Referenz"
      refDescription="Referenz-Audio von der Lehrkraft"
      studentLabel="Dein Song"
      studentDescription="Deine eigene Audio-Datei"
      acceptedFormats="audio/mpeg"
      acceptedMimeTypes={['audio/mpeg']}
      formatDescription="MP3"
      uploadApiEndpoint="/api/tools/mp3-to-midi-feedback/upload"
      cleanupApiEndpoint="/api/tools/mp3-to-midi-feedback/session/cleanup"
      sessionStorageKey="mp3ToMidiSessionId"
      uploadDataStorageKey="mp3ToMidiUploadData"
      errorMessage="Bitte wähle beide Audiodateien aus"
      successMessage="Audio-Dateien erfolgreich hochgeladen!"
      onNext={onNext}
      onBack={() => window.location.href = '/'}
    />
  );
}

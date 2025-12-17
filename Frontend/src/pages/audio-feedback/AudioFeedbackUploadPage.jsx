import GenericUploadPage from '../../components/common/GenericUploadPage'

export default function AudioUpload_Page({ onNext }) {
  return (
    <GenericUploadPage
      title="Audio-Dateien hochladen"
      refLabel="Referenz"
      refDescription="Referenz-Audio von der Lehrkraft"
      studentLabel="Dein Song"
      studentDescription="Deine eigene Audio-Datei"
      acceptedFormats="audio/mpeg"
      acceptedMimeTypes={['audio/mpeg']}
      formatDescription="MP3"
      uploadApiEndpoint="/api/tools/audio-feedback/upload"
      cleanupApiEndpoint="/api/tools/audio-feedback/session/cleanup"
      sessionStorageKey="sessionId"
      uploadDataStorageKey="uploadData"
      errorMessage="Bitte wähle beide Audiodateien aus"
      successMessage="Audio-Dateien erfolgreich hochgeladen!"
      onNext={onNext}
      onBack={() => window.location.href = '/'}
    />
  );
}

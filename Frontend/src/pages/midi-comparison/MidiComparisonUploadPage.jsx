import GenericUploadPage from '../../components/common/GenericUploadPage'

export default function MidiUpload_Page({ onNext }) {
  return (
    <GenericUploadPage
      title="MIDI-Dateien hochladen"
      refLabel="Referenz"
      refDescription="Referenz-MIDI von der Lehrkraft"
      studentLabel="Dein Song"
      studentDescription="Deine eigene MIDI-Datei"
      acceptedFormats=".mid,.midi"
      formatDescription=".mid, .midi"
      uploadApiEndpoint="/api/tools/midi-comparison/upload"
      cleanupApiEndpoint="/api/tools/midi-comparison/session/cleanup"
      sessionStorageKey="midiSessionId"
      uploadDataStorageKey="midiUploadData"
      errorMessage="Bitte wähle beide MIDI-Dateien aus"
      successMessage="MIDI-Dateien erfolgreich hochgeladen!"
      onNext={onNext}
      onBack={() => window.location.href = '/'}
    />
  );
}

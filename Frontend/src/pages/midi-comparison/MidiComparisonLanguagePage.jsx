// MIDI Language Page - Uses CommonLanguagePage with MIDI storage
import CommonLanguagePage from '../common/CommonLanguagePage.jsx';

export default function MidiComparisonLanguagePage({ onBack, onNext }) {
  return <CommonLanguagePage onBack={onBack} onNext={onNext} toolType="midi" />;
}

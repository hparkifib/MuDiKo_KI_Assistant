// MIDI Personalization Page - Uses CommonPersonalizationPage with MIDI storage
import CommonPersonalizationPage from '../common/CommonPersonalizationPage.jsx';

export default function MidiComparisonPersonalizationPage({ onBack, onNext }) {
  return <CommonPersonalizationPage onBack={onBack} onNext={onNext} toolType="midi" />;
}

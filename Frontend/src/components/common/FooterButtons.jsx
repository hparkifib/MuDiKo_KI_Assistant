/**
 * Wiederverwendbare Footer-Button-Container-Komponente.
 * @param {Object} props
 * @param {Function} props.onBack - Handler für Zurück-Button
 * @param {Function} props.onNext - Handler für Weiter-Button
 * @param {string} [props.backLabel='← Zurück'] - Label für Zurück-Button
 * @param {string} [props.nextLabel='Weiter →'] - Label für Weiter-Button
 */
import { footerButtonContainerStyle } from '../../styles/commonStyles';
import Button from './Button';

export default function FooterButtons({ onBack, onNext, backLabel = '← Zurück', nextLabel = 'Weiter →' }) {
  return (
    <div style={footerButtonContainerStyle}>
      <Button variant="secondary" onClick={onBack}>
        {backLabel}
      </Button>
      <Button onClick={onNext}>
        {nextLabel}
      </Button>
    </div>
  );
}

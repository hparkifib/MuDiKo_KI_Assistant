/**
 * Wiederverwendbare Card-Komponente mit Event-Handler-Unterstützung.
 * @param {Object} props
 * @param {React.ReactNode} props.children - Inhalt der Card
 * @param {Object} props.style - Zusätzliche Styles
 * @param {Function} props.onClick - Click-Handler
 * @param {Function} props.onMouseEnter - Mouse-Enter-Handler
 * @param {Function} props.onMouseLeave - Mouse-Leave-Handler
 */
import { cardStyle } from '../../styles/commonStyles';

export default function Card({ children, style = {}, onClick, onMouseEnter, onMouseLeave, ...props }) {
  return (
    <div 
      style={{ ...cardStyle, ...style }}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      {...props}
    >
      {children}
    </div>
  );
}

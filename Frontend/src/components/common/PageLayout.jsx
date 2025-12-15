/**
 * Wiederverwendbare Page-Layout-Komponente für konsistentes Seitenlayout.
 * @param {Object} props
 * @param {React.ReactNode} props.children - Seiteninhalt
 */
import { containerStyle } from '../../styles/commonStyles';

export default function PageLayout({ children }) {
  return (
    <div style={containerStyle}>
      {children}
    </div>
  );
}

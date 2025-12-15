/**
 * Wiederverwendbare Header-Komponente mit Titel und Logo.
 * @param {Object} props
 * @param {string} props.title - Seitentitel
 */
import { headerStyle, titleStyle, logoStyle } from '../../styles/commonStyles';

export default function PageHeader({ title }) {
  return (
    <div style={headerStyle}>
      <h1 style={titleStyle}>{title}</h1>
      <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={logoStyle} />
    </div>
  );
}

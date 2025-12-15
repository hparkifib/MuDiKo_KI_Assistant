/**
 * Wiederverwendbare Button-Komponente mit Hover-Effekten.
 * @param {Object} props
 * @param {React.ReactNode} props.children - Button-Inhalt
 * @param {Function} props.onClick - Click-Handler
 * @param {string} [props.variant='primary'] - Button-Variante ('primary' oder 'secondary')
 * @param {boolean} [props.disabled=false] - Disabled-Status
 * @param {Object} props.style - Zusätzliche Styles
 */
import { buttonStyle, secondaryButtonStyle } from '../../styles/commonStyles';

export default function Button({ 
  children, 
  onClick, 
  variant = 'primary', 
  disabled = false,
  style = {},
  ...props 
}) {
  const baseStyle = variant === 'secondary' ? secondaryButtonStyle : buttonStyle;
  
  const handleMouseEnter = (e) => {
    if (!disabled) {
      e.target.style.transform = 'scale(1.05)';
    }
  };
  
  const handleMouseLeave = (e) => {
    e.target.style.transform = 'scale(1)';
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ 
        ...baseStyle, 
        ...style,
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer'
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {children}
    </button>
  );
}

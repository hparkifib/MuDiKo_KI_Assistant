/**
 * Zentrale Style-Definitionen für konsistente UI-Gestaltung.
 * Alle wiederverwendbaren Komponenten-Styles sind hier definiert.
 */

export const containerStyle = {
  minHeight: '100vh',
  minHeight: '100dvh',
  height: '100dvh',
  width: '100%',
  backgroundColor: 'var(--bg-color)',
  backgroundImage: 'url(/Rainbow-Line.svg)',
  backgroundPosition: 'top',
  backgroundRepeat: 'no-repeat',
  backgroundSize: 'contain',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  alignItems: 'center'
};

export const headerStyle = {
  backgroundColor: 'var(--card-color)',
  borderRadius: '20px',
  padding: '20px',
  marginTop: '20px',
  width: '90%',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
};

export const titleStyle = {
  margin: '0',
  color: 'var(--font-color)',
  fontSize: 'var(--title-font-size)'
};

export const cardStyle = {
  backgroundColor: 'var(--card-color)',
  borderRadius: '20px',
  padding: '20px',
  width: '90%',
  marginTop: '10px'
};

export const buttonStyle = {
  backgroundColor: 'var(--button-color)',
  border: '3px solid',
  borderImage: 'var(--mudiko-gradient) 1',
  color: 'var(--font-color)',
  padding: '15px 30px',
  borderRadius: '0px',
  cursor: 'pointer',
  fontFamily: "'Nunito', sans-serif",
  fontSize: 'var(--button-font-size)',
  fontWeight: 'var(--button-font-weight)',
  boxShadow: 'var(--shadow)',
  transition: 'all 0.3s ease',
  letterSpacing: '1px'
};

export const secondaryButtonStyle = {
  backgroundColor: 'transparent',
  border: '3px solid',
  borderImage: 'var(--mudiko-gradient) 1',
  color: 'var(--font-color)',
  padding: '15px 30px',
  borderRadius: '0px',
  cursor: 'pointer',
  fontFamily: "'Nunito', sans-serif",
  fontSize: 'var(--button-font-size)',
  fontWeight: 'var(--button-font-weight)',
  transition: 'all 0.3s ease',
  letterSpacing: '1px'
};

export const inputStyle = {
  backgroundColor: 'var(--button-color)',
  color: 'var(--font-color)',
  border: 'none',
  borderRadius: '5px',
  padding: '10px',
  fontFamily: "'Nunito', sans-serif",
  fontSize: '16px',
  width: '100%',
  boxSizing: 'border-box'
};

export const selectStyle = {
  backgroundColor: 'var(--button-color)',
  color: 'var(--font-color)',
  border: 'none',
  borderRadius: '5px',
  padding: '5px 10px',
  fontFamily: "'Nunito', sans-serif"
};

export const textStyle = {
  color: 'var(--font-color)',
  margin: '0 0 20px 0'
};

export const logoStyle = {
  width: '60px',
  height: '60px'
};

export const footerButtonContainerStyle = {
  width: '90%',
  display: 'flex',
  justifyContent: 'space-between',
  marginBottom: '20px'
};

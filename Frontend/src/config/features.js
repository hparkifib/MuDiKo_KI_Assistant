/**
 * Feature Flags Configuration
 * 
 * Diese Datei verwaltet alle Feature-Toggles für die Anwendung.
 * Features können über Umgebungsvariablen oder während der Entwicklung
 * direkt hier aktiviert/deaktiviert werden.
 */

export const FEATURES = {
  // LLM Feedback Prototyp - Ermöglicht Segment-basiertes KI-Feedback
  LLM_FEEDBACK_PROTOTYPE: process.env.REACT_APP_ENABLE_LLM_PROTOTYPE === 'true' || true, // Für Entwicklung auf true gesetzt
};

/**
 * Hilfsfunktion zum Prüfen ob ein Feature aktiv ist
 * @param {string} featureName - Name des Features aus FEATURES object
 * @returns {boolean} - true wenn Feature aktiv ist
 */
export const isFeatureEnabled = (featureName) => {
  return FEATURES[featureName] === true;
};

/**
 * Debug-Funktion um alle aktiven Features zu loggen
 */
export const logActiveFeatures = () => {
  if (process.env.NODE_ENV === 'development') {
    console.log('🎯 Aktive Features:', 
      Object.entries(FEATURES)
        .filter(([, enabled]) => enabled)
        .map(([name]) => name)
    );
  }
};
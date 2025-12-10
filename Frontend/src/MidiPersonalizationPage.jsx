// MIDI Personalization Page Wrapper - Uses MIDI-specific storage
import { useState, useEffect } from 'react';
import PersonalizationPage from './PersonalizationPage.jsx';

export default function MidiPersonalizationPage({ onBack, onNext }) {
  // Override localStorage with sessionStorage and MIDI-specific keys
  const originalSetItem = Storage.prototype.setItem;
  const originalGetItem = Storage.prototype.getItem;
  
  useEffect(() => {
    // Intercept localStorage calls and redirect to sessionStorage with midi prefix
    Storage.prototype.setItem = function(key, value) {
      if (key === 'formData') {
        sessionStorage.setItem('midiFormData', value);
      } else {
        originalSetItem.call(this, key, value);
      }
    };
    
    Storage.prototype.getItem = function(key) {
      if (key === 'formData') {
        return sessionStorage.getItem('midiFormData');
      }
      return originalGetItem.call(this, key);
    };
    
    return () => {
      // Restore original methods
      Storage.prototype.setItem = originalSetItem;
      Storage.prototype.getItem = originalGetItem;
    };
  }, []);
  
  return <PersonalizationPage onBack={onBack} onNext={onNext} />;
}

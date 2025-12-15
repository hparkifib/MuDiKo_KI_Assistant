// Custom Hook für Tool-spezifischen Storage (Audio vs MIDI)
import { useEffect } from 'react';

/**
 * Hook für Tool-spezifisches Storage Management
 * Ermöglicht die Verwendung derselben Komponente für Audio und MIDI
 * mit separatem Storage
 * 
 * @param {string} toolType - 'audio' oder 'midi'
 * @returns {object} Storage-Methoden
 */
export function useToolStorage(toolType = 'audio') {
  const storagePrefix = toolType === 'midi' ? 'midi' : '';
  const isMidi = toolType === 'midi';
  
  // Storage-Keys
  const keys = {
    formData: isMidi ? 'midiFormData' : 'formData',
    uploadData: isMidi ? 'midiUploadData' : 'uploadData',
    sessionId: isMidi ? 'midiSessionId' : 'sessionId'
  };
  
  // Storage-Typ: MIDI nutzt sessionStorage, Audio nutzt localStorage
  const storage = isMidi ? sessionStorage : localStorage;
  
  const getItem = (key) => {
    const storageKey = keys[key] || key;
    const value = storage.getItem(storageKey);
    try {
      return value ? JSON.parse(value) : null;
    } catch {
      return value;
    }
  };
  
  const setItem = (key, value) => {
    const storageKey = keys[key] || key;
    const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
    storage.setItem(storageKey, stringValue);
  };
  
  const removeItem = (key) => {
    const storageKey = keys[key] || key;
    storage.removeItem(storageKey);
  };
  
  const clear = () => {
    Object.values(keys).forEach(key => storage.removeItem(key));
  };
  
  return {
    getItem,
    setItem,
    removeItem,
    clear,
    keys,
    storage,
    isMidi
  };
}

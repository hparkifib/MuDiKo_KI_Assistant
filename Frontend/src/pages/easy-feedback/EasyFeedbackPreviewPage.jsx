import { useState, useEffect, useRef, useCallback } from 'react'
import * as Tone from 'tone'
import { Midi } from '@tonejs/midi'

/**
 * Preview-Seite - Zeigt MIDI-Vorschau nach Konvertierung.
 */

// Verfügbare Synthesizer-Klänge
const SYNTH_SOUNDS = [
  { id: 'triangle', name: 'Standard' },
  { id: 'sine', name: 'Sanft' },
  { id: 'square', name: '8-Bit' },
  { id: 'sawtooth', name: 'Scharf' },
];

export default function EasyFeedbackPreviewPage({ onNext, onBack }) {
  // Phase: 'converting' | 'preview' | 'generating' | 'error'
  const [phase, setPhase] = useState('converting');
  const [status, setStatus] = useState('Analysiere Audio...');
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  // MIDI data
  const [refMidi, setRefMidi] = useState(null);
  const [studentMidi, setStudentMidi] = useState(null);
  
  // Playback state
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [playbackProgress, setPlaybackProgress] = useState(0);
  const [playbackDuration, setPlaybackDuration] = useState(0);
  
  // Settings
  const [volume, setVolume] = useState(70);
  const [synthSound, setSynthSound] = useState('triangle');
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [infoContent, setInfoContent] = useState(null);
  
  // Refs
  const synthRef = useRef(null);
  const playbackStartRef = useRef(null);
  const animationFrameRef = useRef(null);
  const currentRoleRef = useRef(null);
  const scheduledTimeoutsRef = useRef([]);
  const isPlayingRef = useRef(false);

  useEffect(() => {
    const storedSessionId = localStorage.getItem('easyFeedbackSessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      startConversion(storedSessionId);
    } else {
      setError('Keine Session gefunden. Bitte lade die Dateien erneut hoch.');
      setPhase('error');
    }

    // Load info content
    fetch('/texts/midi-info-de.json')
      .then(res => res.json())
      .then(data => setInfoContent(data))
      .catch(err => console.error('Failed to load info content:', err));

    return () => {
      stopPlayback();
      disposeSynth();
    };
  }, []);

  // Update volume
  useEffect(() => {
    if (synthRef.current) {
      const dbVolume = (volume / 100) * 30 - 30;
      synthRef.current.volume.value = dbVolume;
    }
  }, [volume]);

  const disposeSynth = () => {
    if (synthRef.current) {
      synthRef.current.dispose();
      synthRef.current = null;
    }
  };

  // ===== CONVERSION =====
  const startConversion = async (sid) => {
    try {
      setStatus('Analysiere Audio-Eigenschaften...');
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setStatus('Konvertiere zu MIDI...');
      
      const response = await fetch('/api/tools/easy-feedback/convert', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Session-ID': sid 
        },
        body: JSON.stringify({ sessionId: sid })
      });
      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Konvertierung fehlgeschlagen');
      }

      setStatus('Lade MIDI-Vorschau...');
      
      await Promise.all([
        loadMidiFile('referenz', sid),
        loadMidiFile('schueler', sid)
      ]);

      setPhase('preview');

    } catch (err) {
      console.error('Conversion error:', err);
      setError(err.message || 'Fehler bei der Konvertierung');
      setPhase('error');
    }
  };

  const loadMidiFile = async (role, sid) => {
    try {
      const response = await fetch(`/api/tools/easy-feedback/midi/${role}?sessionId=${sid}`, {
        headers: { 'X-Session-ID': sid }
      });
      
      if (!response.ok) return;
      
      const arrayBuffer = await response.arrayBuffer();
      const midi = new Midi(arrayBuffer);
      
      if (role === 'referenz') {
        setRefMidi(midi);
      } else {
        setStudentMidi(midi);
      }
    } catch (err) {
      console.error(`Error loading ${role} MIDI:`, err);
    }
  };

  // ===== MIDI PLAYBACK =====
  const createSynth = () => {
    disposeSynth();
    
    const selectedSound = SYNTH_SOUNDS.find(s => s.id === synthSound);
    synthRef.current = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: selectedSound?.id || 'triangle' },
      envelope: {
        attack: 0.02,
        decay: 0.1,
        sustain: 0.3,
        release: 0.8
      }
    }).toDestination();
    
    const dbVolume = (volume / 100) * 30 - 30;
    synthRef.current.volume.value = dbVolume;
  };

  const stopPlayback = useCallback(() => {
    isPlayingRef.current = false;
    
    // Cancel animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    // Clear all scheduled timeouts
    scheduledTimeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    scheduledTimeoutsRef.current = [];
    
    // Release synth
    if (synthRef.current) {
      synthRef.current.releaseAll();
    }
    
    playbackStartRef.current = null;
    currentRoleRef.current = null;
    setCurrentlyPlaying(null);
    setPlaybackProgress(0);
  }, []);

  const playMidi = useCallback(async (role, startTime = 0) => {
    const midiData = role === 'referenz' ? refMidi : studentMidi;
    if (!midiData) return;
    
    // Stop any current playback first
    stopPlayback();
    
    // Start audio context
    if (Tone.context.state !== 'running') {
      await Tone.start();
    }
    
    createSynth();
    
    isPlayingRef.current = true;
    currentRoleRef.current = role;
    setCurrentlyPlaying(role);
    
    // Calculate total duration
    let maxTime = 0;
    midiData.tracks.forEach(track => {
      track.notes.forEach(note => {
        const endTime = note.time + note.duration;
        if (endTime > maxTime) maxTime = endTime;
      });
    });
    setPlaybackDuration(maxTime);
    setPlaybackProgress(startTime);
    
    // Store start time
    const audioStartTime = Tone.now();
    playbackStartRef.current = audioStartTime - startTime;
    
    // Schedule notes
    midiData.tracks.forEach(track => {
      track.notes.forEach(note => {
        if (note.time + note.duration < startTime) return;
        
        const adjustedTime = note.time - startTime;
        if (adjustedTime < 0) {
          const remainingDuration = note.duration + adjustedTime;
          if (remainingDuration > 0 && synthRef.current) {
            synthRef.current.triggerAttackRelease(
              note.name,
              remainingDuration,
              audioStartTime,
              note.velocity
            );
          }
        } else {
          const timeout = setTimeout(() => {
            if (isPlayingRef.current && synthRef.current && currentRoleRef.current === role) {
              synthRef.current.triggerAttackRelease(
                note.name,
                note.duration,
                undefined,
                note.velocity
              );
            }
          }, adjustedTime * 1000);
          scheduledTimeoutsRef.current.push(timeout);
        }
      });
    });

    // Progress update using requestAnimationFrame
    const updateProgress = () => {
      if (!isPlayingRef.current || !playbackStartRef.current) return;
      
      const elapsed = Tone.now() - playbackStartRef.current;
      setPlaybackProgress(Math.min(elapsed, maxTime));
      
      if (elapsed >= maxTime) {
        stopPlayback();
      } else {
        animationFrameRef.current = requestAnimationFrame(updateProgress);
      }
    };
    
    animationFrameRef.current = requestAnimationFrame(updateProgress);
  }, [refMidi, studentMidi, stopPlayback, synthSound, volume]);

  const seekTo = useCallback((role, time) => {
    playMidi(role, time);
  }, [playMidi]);

  // ===== GENERATE FEEDBACK =====
  const handleGenerateFeedback = async () => {
    if (!sessionId) return;
    
    stopPlayback();
    setPhase('generating');
    setStatus('Vergleiche MIDI-Dateien...');

    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const compareResponse = await fetch('/api/tools/easy-feedback/compare', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId 
        },
        body: JSON.stringify({ sessionId })
      });
      const compareResult = await compareResponse.json();

      if (!compareResult.success) {
        throw new Error(compareResult.error || 'Vergleich fehlgeschlagen');
      }

      setStatus('Generiere Feedback-Prompt...');
      await new Promise(resolve => setTimeout(resolve, 300));

      const generateResponse = await fetch('/api/tools/easy-feedback/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId 
        },
        body: JSON.stringify({ sessionId })
      });
      const generateResult = await generateResponse.json();

      if (!generateResult.success) {
        throw new Error(generateResult.error || 'Prompt-Generierung fehlgeschlagen');
      }

      localStorage.setItem('easyFeedbackResult', JSON.stringify({
        system_prompt: generateResult.system_prompt,
        user_prompt: generateResult.user_prompt
      }));

      setStatus('Fertig!');
      setTimeout(() => onNext && onNext(), 500);

    } catch (err) {
      console.error('Generation error:', err);
      setError(err.message || 'Fehler bei der Verarbeitung');
      setPhase('error');
    }
  };

  // ===== HELPER =====
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getNoteCount = (midi) => {
    if (!midi) return 0;
    return midi.tracks.reduce((sum, t) => sum + t.notes.length, 0);
  };

  // ===== RENDER: Info Modal =====
  const InfoModal = () => {
    if (!showInfoModal || !infoContent) return null;

    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
        padding: '20px'
      }} onClick={() => setShowInfoModal(false)}>
        <div style={{
          backgroundColor: 'var(--card-color)',
          borderRadius: '20px',
          padding: '25px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          position: 'relative'
        }} onClick={e => e.stopPropagation()}>
          {/* Close Button */}
          <button
            onClick={() => setShowInfoModal(false)}
            style={{
              position: 'absolute',
              top: '15px',
              right: '15px',
              background: 'var(--button-color)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              fontSize: '18px',
              color: 'var(--font-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>

          <h2 style={{ 
            color: 'var(--font-color)', 
            margin: '0 0 20px 0',
            fontSize: '20px',
            paddingRight: '40px'
          }}>
            💡 {infoContent.title}
          </h2>

          {infoContent.sections.map((section, idx) => (
            <div key={idx} style={{ marginBottom: '20px' }}>
              <h3 style={{ 
                color: 'var(--mudiko-cyan)', 
                margin: '0 0 8px 0',
                fontSize: '15px'
              }}>
                {section.heading}
              </h3>
              <p style={{ 
                color: 'var(--font-color)', 
                margin: '0',
                fontSize: '14px',
                lineHeight: '1.6',
                opacity: 0.9
              }}>
                {section.content}
              </p>
              {section.list && (
                <ul style={{ 
                  margin: '8px 0 0 0', 
                  paddingLeft: '20px',
                  color: 'var(--font-color)',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  opacity: 0.9
                }}>
                  {section.list.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // ===== RENDER: Loading =====
  if (phase === 'converting' || phase === 'generating') {
    return (
      <div style={{ 
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
      }}>
        <InfoModal />
        
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Header with Info Button */}
          <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>
              {phase === 'converting' ? 'MIDI-Konvertierung' : 'Feedback generieren'}
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={() => setShowInfoModal(true)}
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  border: 'none',
                  backgroundColor: 'var(--mudiko-cyan)',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Was ist MIDI?"
              >
                💡
              </button>
              <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
            </div>
          </div>

          <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ 
                display: 'inline-block',
                width: '50px',
                height: '50px',
                border: '4px solid var(--button-color)',
                borderTop: '4px solid var(--mudiko-pink)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                marginBottom: '20px'
              }} />
              <h3 style={{ color: 'var(--font-color)', margin: '0 0 10px 0' }}>
                🎹 {status}
              </h3>
              <p style={{ color: 'var(--font-color)', margin: '0 0 20px 0', opacity: 0.8 }}>
                {phase === 'converting' 
                  ? 'Die Audio-Dateien werden analysiert und zu MIDI konvertiert.'
                  : 'Die MIDI-Dateien werden verglichen und der Prompt wird erstellt.'}
              </p>
              
              {/* Info hint */}
              <p 
                onClick={() => setShowInfoModal(true)}
                style={{ 
                  color: 'var(--mudiko-cyan)', 
                  margin: '0', 
                  fontSize: '14px',
                  cursor: 'pointer',
                  opacity: 0.9
                }}
              >
                💡 Du willst wissen, was hier passiert? Klicke auf die Lampe!
              </p>
            </div>
          </div>
        </div>

        <div style={{ height: '20px' }} />

        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // ===== RENDER: Error =====
  if (phase === 'error') {
    return (
      <div style={{ 
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
      }}>
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>Fehler</h1>
            <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
          </div>
          <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px' }}>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <p style={{ color: '#ff6b6b', fontSize: '16px' }}>⚠️ {error}</p>
              <button
                onClick={() => onBack && onBack()}
                style={{
                  backgroundColor: 'var(--button-color)',
                  color: 'var(--font-color)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 30px',
                  fontSize: '16px',
                  cursor: 'pointer',
                  fontFamily: "'Nunito', sans-serif",
                  marginTop: '15px'
                }}
              >
                Zurück zum Upload
              </button>
            </div>
          </div>
        </div>
        <div style={{ height: '20px' }} />
      </div>
    );
  }

  // ===== HELPER: Get MIDI duration =====
  const getMidiDuration = (midi) => {
    if (!midi) return 0;
    return Math.max(...midi.tracks.flatMap(t => t.notes.map(n => n.time + n.duration)), 0);
  };

  // ===== HANDLER: Play/Stop =====
  const handlePlayStop = (role) => {
    if (currentlyPlaying === role) {
      stopPlayback();
    } else {
      const midi = role === 'referenz' ? refMidi : studentMidi;
      if (midi) playMidi(role);
    }
  };

  // ===== HANDLER: Seek =====
  const handleSeek = (e, role, duration) => {
    if (duration === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percent = clickX / rect.width;
    const seekTime = percent * duration;
    seekTo(role, seekTime);
  };

  // ===== RENDER: MIDI Player Component =====
  const renderMidiPlayer = (role, midi, color) => {
    const isPlaying = currentlyPlaying === role;
    const noteCount = getNoteCount(midi);
    const duration = getMidiDuration(midi);
    const progress = isPlaying ? playbackProgress : 0;
    const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;

    if (!midi) {
      return (
        <div style={{ 
          backgroundColor: `${color}15`,
          borderRadius: '12px',
          padding: '12px 15px',
          marginBottom: '10px',
          border: `2px solid ${color}`,
          opacity: 0.5
        }}>
          <p style={{ color: 'var(--font-color)', margin: 0, textAlign: 'center', fontSize: '14px' }}>
            Keine MIDI-Daten verfügbar
          </p>
        </div>
      );
    }

    return (
      <div style={{ 
        backgroundColor: `${color}15`,
        borderRadius: '12px',
        padding: '12px 15px',
        marginBottom: '10px',
        border: `2px solid ${color}`
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ color: 'var(--font-color)', fontSize: '14px', fontWeight: '600' }}>
            {role === 'referenz' ? '🎵 Referenz' : '🎤 Schüler'}
          </span>
          <span style={{ color, fontSize: '12px' }}>
            {noteCount} Noten
          </span>
        </div>

        {/* Player Row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Play/Stop */}
          <button
            onClick={() => handlePlayStop(role)}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              border: 'none',
              backgroundColor: isPlaying ? '#ff6b6b' : color,
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              flexShrink: 0
            }}
          >
            {isPlaying ? '⏹' : '▶'}
          </button>

          {/* Time */}
          <span style={{ 
            color: 'var(--font-color)', 
            fontSize: '11px', 
            opacity: 0.8, 
            minWidth: '32px',
            fontFamily: 'monospace'
          }}>
            {formatTime(progress)}
          </span>

          {/* Progress Bar (clickable) */}
          <div 
            onClick={(e) => handleSeek(e, role, duration)}
            style={{ 
              flex: 1, 
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer'
            }}
          >
            <div style={{ 
              width: '100%', 
              height: '6px', 
              backgroundColor: 'var(--button-color)', 
              borderRadius: '3px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{ 
                width: `${progressPercent}%`, 
                height: '100%', 
                backgroundColor: color,
                transition: isPlaying ? 'none' : 'width 0.1s'
              }} />
            </div>
          </div>

          {/* Duration */}
          <span style={{ 
            color: 'var(--font-color)', 
            fontSize: '11px', 
            opacity: 0.8, 
            minWidth: '32px',
            fontFamily: 'monospace'
          }}>
            {formatTime(duration)}
          </span>
        </div>
      </div>
    );
  };

  // ===== RENDER: Preview =====
  return (
    <div style={{ 
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
    }}>
      <InfoModal />
      
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, overflow: 'auto' }}>
        {/* Header */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', marginTop: '20px', width: '90%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: '0', color: 'var(--font-color)', fontSize: 'var(--title-font-size)' }}>MIDI-Vorschau</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => setShowInfoModal(true)}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: 'none',
                backgroundColor: 'var(--mudiko-cyan)',
                color: 'white',
                cursor: 'pointer',
                fontSize: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title="Was ist MIDI?"
            >
              💡
            </button>
            <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ width: '60px', height: '60px' }} />
          </div>
        </div>

        {/* Content */}
        <div style={{ backgroundColor: 'var(--card-color)', borderRadius: '20px', padding: '20px', width: '90%', marginTop: '10px', marginBottom: '20px' }}>
          
          {/* Controls Row */}
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '15px',
            gap: '15px'
          }}>
            {/* Sound Selection */}
            <select
              value={synthSound}
              onChange={(e) => setSynthSound(e.target.value)}
              style={{
                backgroundColor: 'var(--button-color)',
                color: 'var(--font-color)',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 12px',
                fontSize: '13px',
                cursor: 'pointer',
                fontFamily: "'Nunito', sans-serif"
              }}
            >
              {SYNTH_SOUNDS.map(sound => (
                <option key={sound.id} value={sound.id}>🎹 {sound.name}</option>
              ))}
            </select>

            {/* Volume */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '16px' }}>🔊</span>
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(parseInt(e.target.value))}
                style={{ 
                  width: '80px',
                  accentColor: 'var(--mudiko-pink)',
                  cursor: 'pointer'
                }}
              />
            </div>
          </div>

          {/* MIDI Players */}
          {renderMidiPlayer('referenz', refMidi, 'var(--mudiko-cyan)')}
          {renderMidiPlayer('schueler', studentMidi, 'var(--mudiko-pink)')}

        </div>
      </div>

      {/* Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '95%', padding: '20px 0', flexShrink: 0 }}>
        <button
          onClick={() => {
            stopPlayback();
            onBack && onBack();
          }}
          style={{
            backgroundColor: 'var(--button-color)',
            color: 'var(--font-color)',
            border: '2px solid #666666',
            padding: '12px 24px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          ← Zurück
        </button>
        <button
          onClick={handleGenerateFeedback}
          disabled={!refMidi || !studentMidi}
          style={{
            backgroundColor: 'var(--button-color)',
            border: '3px solid',
            borderImage: 'var(--mudiko-gradient) 1',
            color: 'var(--font-color)',
            padding: '15px 30px',
            borderRadius: '0px',
            cursor: (!refMidi || !studentMidi) ? 'not-allowed' : 'pointer',
            fontFamily: "'Nunito', sans-serif",
            fontSize: 'var(--button-font-size)',
            fontWeight: 'var(--button-font-weight)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease',
            letterSpacing: '1px',
            opacity: (!refMidi || !studentMidi) ? 0.5 : 1
          }}
          onMouseEnter={(e) => { if (refMidi && studentMidi) e.target.style.transform = 'scale(1.05)' }}
          onMouseLeave={(e) => { if (refMidi && studentMidi) e.target.style.transform = 'scale(1)' }}
        >
          Weiter
        </button>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

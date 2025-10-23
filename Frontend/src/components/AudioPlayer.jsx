import React, { useState, useRef, useEffect } from 'react';

export default function AudioPlayer({ uploadData, segments = [], onTimeUpdate }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const audioRef = useRef(null);

  // Hilfsfunktion für Audio-URL (gleich wie in RecordingsPage)
  const getAudioUrl = (filename) => {
    return `/api/audio/${filename}`;
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setIsLoading(false);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
      // Callback für Segment-Synchronisation
      if (onTimeUpdate) {
        onTimeUpdate(audio.currentTime);
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleLoadStart = () => {
      setIsLoading(true);
    };

    const handleCanPlay = () => {
      setIsLoading(false);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('loadstart', handleLoadStart);
    audio.addEventListener('canplay', handleCanPlay);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('loadstart', handleLoadStart);
      audio.removeEventListener('canplay', handleCanPlay);
    };
  }, [onTimeUpdate]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const audio = audioRef.current;
    if (!audio) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (e) => {
    const audio = audioRef.current;
    const newVolume = parseFloat(e.target.value);
    
    setVolume(newVolume);
    if (audio) {
      audio.volume = newVolume;
    }
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const seekToSegment = (segment) => {
    const audio = audioRef.current;
    if (!audio || !segment.startTime) return;

    audio.currentTime = segment.startTime;
    setCurrentTime(segment.startTime);
    
    // Auto-Play wenn Segment angeklickt wird
    if (!isPlaying) {
      audio.play();
      setIsPlaying(true);
    }
  };

  // Expose seekToSegment function to parent component via global reference
  useEffect(() => {
    window.audioPlayerRef = {
      seekToSegment: seekToSegment
    };
    
    return () => {
      // Cleanup global reference on unmount
      if (window.audioPlayerRef) {
        delete window.audioPlayerRef;
      }
    };
  }, []);

  if (!uploadData || !uploadData.file_map || !uploadData.file_map.referenz) {
    return (
      <div style={{
        backgroundColor: 'var(--card-color)',
        borderRadius: '20px',
        padding: '20px',
        textAlign: 'center',
        color: 'var(--font-color)'
      }}>
        <div style={{ marginBottom: '15px' }}>
          ⚠️ Keine Audio-Datei geladen
        </div>
        <div style={{ fontSize: '14px', opacity: 0.7 }}>
          Bitte lade zuerst eine Referenz-Audio-Datei hoch.
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'var(--card-color)',
      borderRadius: '15px', // Reduziert von 20px
      padding: '12px', // Reduziert von 20px
      boxShadow: 'var(--shadow)'
    }}>
      {/* Hidden HTML5 Audio Element */}
      <audio
        ref={audioRef}
        preload="metadata"
      >
        <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/mpeg" />
        <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/wav" />
        <source src={getAudioUrl(uploadData.file_map.referenz)} type="audio/mp4" />
        Ihr Browser unterstützt das Audio-Element nicht.
      </audio>

      {/* Audio Player UI */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px' // Reduziert von 15px
      }}>
        
        {/* File Info */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px', // Reduziert von 10px
          marginBottom: '5px' // Reduziert von 10px
        }}>
          <div style={{
            width: '6px', // Reduziert von 8px
            height: '6px',
            borderRadius: '50%',
            backgroundColor: 'var(--mudiko-cyan)',
          }} />
          <h3 style={{ 
            color: 'var(--font-color)', 
            margin: '0', 
            fontSize: '14px', // Reduziert von 16px
            fontWeight: '600' 
          }}>
            🎵 Referenz-Audio
          </h3>
          {isLoading && (
            <div style={{ 
              fontSize: '10px', // Reduziert von 12px
              color: 'var(--mudiko-pink)',
              fontWeight: 'bold' 
            }}>
              Lädt...
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div style={{
          position: 'relative',
          width: '100%',
          height: '6px', // Reduziert von 8px
          backgroundColor: 'var(--button-color)',
          borderRadius: '3px', // Reduziert von 4px
          cursor: 'pointer',
          overflow: 'hidden'
        }}
        onClick={handleSeek}
        >
          {/* Progress Fill */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            height: '100%',
            width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%`,
            background: 'linear-gradient(90deg, var(--mudiko-pink), var(--mudiko-cyan))',
            borderRadius: '3px', // Reduziert von 4px
            transition: 'width 0.1s ease'
          }} />
          
          {/* Segment Markers */}
          {segments.map((segment, index) => (
            <div
              key={index}
              style={{
                position: 'absolute',
                top: '-1px', // Reduziert von -2px
                left: `${duration > 0 ? (segment.startTime / duration) * 100 : 0}%`,
                width: '2px',
                height: '8px', // Reduziert von 12px
                backgroundColor: segment.color || '#ffffff',
                opacity: 0.8,
                pointerEvents: 'none'
              }}
            />
          ))}
        </div>

        {/* Controls Row */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '10px' // Reduziert von 15px
        }}>
          
          {/* Play/Pause Button */}
          <button
            onClick={togglePlayPause}
            disabled={isLoading}
            style={{
              backgroundColor: isPlaying ? 'var(--mudiko-pink)' : 'var(--mudiko-cyan)',
              border: 'none',
              borderRadius: '50%',
              width: '40px', // Reduziert von 50px
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              boxShadow: 'var(--shadow)',
              transition: 'all 0.3s ease',
              opacity: isLoading ? 0.5 : 1
            }}
            onMouseEnter={(e) => !isLoading && (e.target.style.transform = 'scale(1.1)')}
            onMouseLeave={(e) => !isLoading && (e.target.style.transform = 'scale(1)')}
          >
            <span style={{ 
              color: 'white', 
              fontSize: '16px', // Reduziert von 20px
              fontWeight: 'bold',
              marginLeft: isPlaying ? '0' : '2px' // Slight adjustment for play icon
            }}>
              {isLoading ? '⏳' : (isPlaying ? '⏸' : '▶')}
            </span>
          </button>

          {/* Time Display */}
          <div style={{
            color: 'var(--font-color)',
            fontSize: '12px', // Reduziert von 14px
            fontFamily: 'monospace',
            minWidth: '70px', // Reduziert von 80px
            textAlign: 'center'
          }}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>

          {/* Volume Control */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px', // Reduziert von 8px
            flex: 1,
            maxWidth: '100px' // Reduziert von 120px
          }}>
            <span style={{ color: 'var(--font-color)', fontSize: '14px' }}>
              {volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}
            </span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              style={{
                flex: 1,
                height: '3px', // Reduziert von 4px
                backgroundColor: 'var(--button-color)',
                borderRadius: '1.5px', // Reduziert von 2px
                outline: 'none',
                cursor: 'pointer'
              }}
            />
          </div>
        </div>

        {/* Additional Info */}
        <div style={{
          fontSize: '10px', // Reduziert von 12px
          color: 'var(--font-color)',
          opacity: 0.6,
          textAlign: 'center'
        }}>
          Datei: {uploadData.file_map.referenz}
        </div>
      </div>
    </div>
  );
}
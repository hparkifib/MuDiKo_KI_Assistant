import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';

const AudioPlayer = forwardRef(({ uploadData, segments = [], activeSegment, currentSegment, onSegmentClick, onTimeUpdate }, ref) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const audioRef = useRef(null);

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    seekToSegment: (segment) => {
      if (audioRef.current) {
        audioRef.current.currentTime = segment.startTime;
        setCurrentTime(segment.startTime);
      }
    }
  }));

  // Make ref available globally for LLMFeedbackPrototype
  useEffect(() => {
    if (ref) {
      window.audioPlayerRef = {
        seekToSegment: (segment) => {
          if (audioRef.current) {
            audioRef.current.currentTime = segment.startTime;
            setCurrentTime(segment.startTime);
          }
        }
      };
    }
  }, [ref]);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const current = audioRef.current.currentTime;
      setCurrentTime(current);
      if (onTimeUpdate) {
        onTimeUpdate(current);
      }
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const progressBar = e.currentTarget;
    const rect = progressBar.getBoundingClientRect();
    const percentage = (e.clientX - rect.left) / rect.width;
    const newTime = percentage * duration;
    
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getAudioUrl = () => {
    if (!uploadData?.file_map?.schueler) return null;
    return `/api/audio/${uploadData.file_map.schueler}`;
  };

  const audioUrl = getAudioUrl();

  if (!audioUrl) {
    return (
      <div style={{
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        borderRadius: '10px',
        padding: '20px',
        border: '2px solid #ff6b6b',
        textAlign: 'center'
      }}>
        <p style={{ color: '#ff6b6b', margin: '0', fontWeight: '600' }}>
          ⚠️ Keine Audio-Datei verfügbar
        </p>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'var(--button-color)',
      borderRadius: '15px',
      padding: '20px',
      border: '2px solid rgba(255,255,255,0.1)',
      boxShadow: 'var(--shadow)'
    }}>
      {/* Audio Element (hidden) */}
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
        preload="metadata"
      />

      {/* Segment Buttons - oben integriert */}
      {segments.length > 0 && (
        <div style={{
          display: 'flex',
          width: '100%',
          height: '40px',
          marginBottom: '15px',
          gap: '2px',
          borderRadius: '8px',
          overflow: 'hidden',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          {segments.map((segment) => {
            const isCurrentSegment = currentSegment && currentSegment.id === segment.id;
            const isActiveSegment = activeSegment && activeSegment.id === segment.id;
            
            return (
              <button
                key={segment.id}
                onClick={() => onSegmentClick && onSegmentClick(segment)}
                style={{
                  flex: 1,
                  backgroundColor: segment.color,
                  border: 'none',
                  cursor: 'pointer',
                  height: '100%',
                  transition: 'all 0.3s ease',
                  opacity: isActiveSegment ? 1 : 0.85,
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  outline: isCurrentSegment 
                    ? '3px solid #ffffff' 
                    : isActiveSegment 
                      ? '3px solid #ffeb3b' 
                      : 'none',
                  outlineOffset: '-3px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.opacity = '1';
                  e.target.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  if (!isActiveSegment) {
                    e.target.style.opacity = '0.85';
                  }
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                {/* Emoji */}
                <span style={{
                  fontSize: '20px',
                  lineHeight: '1',
                  textShadow: '1px 1px 2px rgba(0,0,0,0.3)'
                }}>
                  {segment.emoji}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Progress Bar - unter den Segment Buttons */}
      <div
        onClick={handleSeek}
        style={{
          width: '100%',
          height: '8px',
          backgroundColor: 'rgba(255,255,255,0.2)',
          borderRadius: '4px',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '15px'
        }}
      >
        {/* Progress Fill */}
        <div
          style={{
            width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%',
            height: '100%',
            backgroundColor: 'var(--mudiko-pink)',
            borderRadius: '4px',
            transition: 'width 0.1s ease'
          }}
        />
        
        {/* Segment Markers in Progress Bar */}
        {segments.map((segment) => (
          <div
            key={`marker-${segment.id}`}
            style={{
              position: 'absolute',
              left: duration > 0 ? `${(segment.startTime / duration) * 100}%` : '0%',
              width: duration > 0 ? `${((segment.endTime - segment.startTime) / duration) * 100}%` : '0%',
              height: '100%',
              backgroundColor: segment.color,
              opacity: 0.4,
              borderRadius: '2px',
              pointerEvents: 'none'
            }}
          />
        ))}
        
        {/* Segment Separators */}
        {segments.slice(0, -1).map((segment, index) => (
          <div
            key={`separator-${segment.id}`}
            style={{
              position: 'absolute',
              left: duration > 0 ? `${(segment.endTime / duration) * 100}%` : '0%',
              width: '1px',
              height: '100%',
              backgroundColor: 'rgba(255,255,255,0.6)',
              pointerEvents: 'none'
            }}
          />
        ))}
      </div>

      {/* Controls Row - UNTEN unter der Progress Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '15px'
      }}>
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          style={{
            backgroundColor: 'var(--button-color)',
            border: '2px solid rgba(255,255,255,0.2)',
            borderRadius: '50%',
            width: '50px',
            height: '50px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: '18px',
            color: 'var(--font-color)',
            boxShadow: 'var(--shadow)',
            transition: 'all 0.3s ease',
            flexShrink: 0
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
            e.target.style.borderColor = 'rgba(255,255,255,0.4)';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'var(--button-color)';
            e.target.style.borderColor = 'rgba(255,255,255,0.2)';
          }}
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>

        {/* Volume Control */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          flexShrink: 0
        }}>
          <span style={{ fontSize: '16px', color: 'rgba(255,255,255,0.7)' }}>🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            style={{
              width: '80px',
              height: '4px',
              borderRadius: '2px',
              background: `linear-gradient(to right, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0.6) ${volume * 100}%, rgba(255,255,255,0.2) ${volume * 100}%, rgba(255,255,255,0.2) 100%)`,
              outline: 'none',
              cursor: 'pointer',
              appearance: 'none',
              WebkitAppearance: 'none'
            }}
          />
        </div>

        {/* Time Display */}
        <div style={{
          color: 'var(--font-color)',
          fontSize: '14px',
          fontWeight: '600',
          flexShrink: 0,
          minWidth: '80px'
        }}>
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      {/* Audio Info */}
      <div style={{
        marginTop: '10px',
        fontSize: '12px',
        color: 'rgba(255,255,255,0.7)',
        textAlign: 'center'
      }}>
        🎵 {uploadData?.original_filenames?.schueler || 'Deine Aufnahme'}
      </div>

      {/* Custom Range Slider Styles */}
      <style>{`
        input[type="range"]::-webkit-slider-thumb {
          appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: rgba(255,255,255,0.8);
          cursor: pointer;
          border: 1px solid rgba(255,255,255,0.3);
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          transition: all 0.2s ease;
        }
        
        input[type="range"]::-webkit-slider-thumb:hover {
          background: rgba(255,255,255,1);
          transform: scale(1.1);
        }
        
        input[type="range"]::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: rgba(255,255,255,0.8);
          cursor: pointer;
          border: 1px solid rgba(255,255,255,0.3);
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  );
});

AudioPlayer.displayName = 'AudioPlayer';

export default AudioPlayer;

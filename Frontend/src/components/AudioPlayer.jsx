import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import playIcon from '../assets/playbutton.svg';
import pauseIcon from '../assets/pausebutton.svg';
import volumeIcon from '../assets/Lautstärkeregler.svg';

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
    const sessionId = (uploadData && uploadData.sessionId) || localStorage.getItem('sessionId');
    if (!sessionId) return null;
    const filename = encodeURIComponent(uploadData.file_map.schueler);
    return `/api/audio/${filename}?sessionId=${encodeURIComponent(sessionId)}`;
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
      backgroundColor: '#3D3D3D',
      borderRadius: '15px',
      padding: '20px',
      border: '2px solid rgba(255,255,255,0.1)',
      boxShadow: 'var(--shadow)',
      height: '120px', // Feste Höhe
      display: 'flex',
      flexDirection: 'column',
      position: 'relative' // Für absolute Positionierung der Segmente
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

      {/* Segment Buttons - herausragend aus dem Container */}
      {segments.length > 0 && (
        <div style={{
          display: 'flex',
          width: 'calc(100% - 40px)', // Anpassung an AudioPlayer-Breite (minus Padding)
          gap: '8px',
          alignItems: 'flex-start', // Emojis oben ausrichten - wachsen nach unten
          position: 'absolute',
          top: '-40px', // Herausragen aus dem Container
          left: '20px', // Container-Padding berücksichtigen
          zIndex: 10 // Über anderen Elementen
        }}>
          {segments.map((segment) => {
            const isCurrentSegment = currentSegment && currentSegment.id === segment.id;
            const isActiveSegment = activeSegment && activeSegment.id === segment.id;
            
            return (
              <div
                key={segment.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  flex: 1,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  alignSelf: 'flex-start' // Jedes Segment startet oben und wächst nach unten
                }}
                onClick={() => onSegmentClick && onSegmentClick(segment)}
              >
                {/* Emoji Container mit farbigem Hintergrund */}
                <div style={{
                  backgroundColor: segment.bgColor,
                  borderRadius: '20px',
                  width: isActiveSegment ? '70px' : '60px',
                  height: isActiveSegment ? '70px' : '60px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '15px', // Mehr Abstand zum Container
                  transition: 'all 0.3s ease',
                  border: isCurrentSegment ? '3px solid #ffffff' : 'none',
                  boxShadow: isActiveSegment ? 'var(--shadow)' : '2px 2px 8px rgba(0,0,0,0.3)' // Schatten für bessere Sichtbarkeit
                }}>
                  <img 
                    src={segment.segmentEmoji || segment.emoji} 
                    alt={`${segment.feedback} emoji`}
                    style={{
                      width: isActiveSegment ? '35px' : '30px',
                      height: isActiveSegment ? '35px' : '30px',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>
                
                {/* Flacher Button darunter */}
                <div style={{
                  width: '100%',
                  height: '8px',
                  backgroundColor: segment.color,
                  borderRadius: '4px',
                  opacity: isActiveSegment ? 1 : 0.7,
                  transition: 'all 0.3s ease'
                }} />
              </div>
            );
          })}
        </div>
      )}

      {/* Platz für herausragende Segmente */}
      <div style={{ marginTop: '25px' }} />

      {/* Progress Bar - unter den Segment Buttons */}
      <div
        onClick={handleSeek}
        style={{
          width: '100%',
          height: '20px',
          backgroundColor: 'rgba(255,255,255,0.3)',
          borderRadius: '10px',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '15px'
        }}
      >
        {/* Segment Background Colors - Hintergrundfarben der Segmente */}
        {segments.map((segment) => (
          <div
            key={`background-${segment.id}`}
            style={{
              position: 'absolute',
              left: duration > 0 ? `${(segment.startTime / duration) * 100}%` : '0%',
              width: duration > 0 ? `${((segment.endTime - segment.startTime) / duration) * 100}%` : '0%',
              height: '100%',
              backgroundColor: segment.bgColor,
              opacity: 0.6,
              borderRadius: '8px',
              pointerEvents: 'none'
            }}
          />
        ))}

        {/* Progress Fill */}
        <div
          style={{
            width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%',
            height: '100%',
            backgroundColor: 'var(--mudiko-pink)',
            borderRadius: '10px',
            transition: 'width 0.1s ease',
            position: 'relative',
            zIndex: 2
          }}
        />
        
        {/* Segment Separators */}
        {segments.slice(0, -1).map((segment, index) => (
          <div
            key={`separator-${segment.id}`}
            style={{
              position: 'absolute',
              left: duration > 0 ? `${(segment.endTime / duration) * 100}%` : '0%',
              width: '1px',
              height: '100%',
              backgroundColor: 'white',
              pointerEvents: 'none',
              zIndex: 3
            }}
          />
        ))}
      </div>

      {/* Controls Row - UNTEN unter der Progress Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '15px',
        marginTop: 'auto' // Push nach unten im Flex-Container
      }}>
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '50%',
            width: '50px',
            height: '50px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            flexShrink: 0,
            padding: '0'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'scale(1)';
          }}
        >
          <img 
            src={isPlaying ? pauseIcon : playIcon} 
            alt={isPlaying ? 'Pause' : 'Play'}
            style={{
              width: '16px',
              height: '18px',
              filter: 'brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)'
            }}
          />
        </button>

        {/* Volume Control */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          flexShrink: 0
        }}>
          <img 
            src={volumeIcon} 
            alt="Volume"
            style={{
              width: '16px',
              height: '16px',
              filter: 'brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)'
            }}
          />
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
              background: `linear-gradient(to right, white 0%, white ${volume * 100}%, rgba(255,255,255,0.2) ${volume * 100}%, rgba(255,255,255,0.2) 100%)`,
              outline: 'none',
              cursor: 'pointer',
              appearance: 'none',
              WebkitAppearance: 'none'
            }}
          />
        </div>

        {/* Time Display */}
        <div style={{
          color: 'white',
          fontSize: '14px',
          fontWeight: '600',
          flexShrink: 0,
          minWidth: '80px'
        }}>
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      {/* Custom Range Slider Styles */}
      <style>{`
        input[type="range"]::-webkit-slider-thumb {
          appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 1px solid white;
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          transition: all 0.2s ease;
        }
        
        input[type="range"]::-webkit-slider-thumb:hover {
          background: white;
          transform: scale(1.1);
        }
        
        input[type="range"]::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 1px solid white;
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  );
});

AudioPlayer.displayName = 'AudioPlayer';

export default AudioPlayer;

import React, { useState, useEffect, useRef } from 'react';
import AudioPlayer from './components/AudioPlayer.jsx';

export default function LLMFeedbackPrototype({ onBack }) {
  const [isLoading, setIsLoading] = useState(true);
  const [uploadData, setUploadData] = useState(null);
  const [segments, setSegments] = useState([]);
  const [activeSegment, setActiveSegment] = useState(null);
  const [currentSegment, setCurrentSegment] = useState(null); // Aktuell spielendes Segment
  const [chatMessages, setChatMessages] = useState({}); // Chat-Messages pro Segment {segmentId: [messages]}
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
  const [llmError, setLlmError] = useState(null);
  const [llmStatus, setLlmStatus] = useState(null);
  const chatMessagesRef = useRef(null);

    // Auto-scroll zu neuesten Nachrichten
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages, activeSegment]);

  // Load saved data on component mount
  useEffect(() => {
    initializeData();
  }, []);

  // Auto-open ersten Segment Chat beim Start
  useEffect(() => {
    if (segments.length > 0 && !activeSegment) {
      setActiveSegment(segments[0]); // Erstes Segment automatisch öffnen
    }
  }, [segments, activeSegment]);

  const initializeData = async () => {
    try {
      // LLM Status abrufen
      await checkLLMStatus();
      
      // Load upload data from localStorage (similar to RecordingsPage)
      const storedUploadData = localStorage.getItem('uploadData');
      
      if (storedUploadData) {
        const uploadDataObj = JSON.parse(storedUploadData);
        setUploadData(uploadDataObj);
        
        // Segment-Analyse und initiales Feedback laden
        const mockSegments = [
          { id: 1, startTime: 0, endTime: 24, feedback: 'good', emoji: '😊', color: '#4CAF50' },
          { id: 2, startTime: 24, endTime: 48, feedback: 'critical', emoji: '😟', color: '#F44336' },
          { id: 3, startTime: 48, endTime: 72, feedback: 'neutral', emoji: '😐', color: '#FF9800' },
          { id: 4, startTime: 72, endTime: 96, feedback: 'good', emoji: '😊', color: '#4CAF50' },
          { id: 5, startTime: 96, endTime: 120, feedback: 'neutral', emoji: '😐', color: '#FF9800' }
        ];
        setSegments(mockSegments);

        // Initiales LLM Feedback für jedes Segment laden
        // Immer Mock-Daten im Demo-Modus verwenden
        loadMockFeedback(mockSegments);
        
        // Zusätzlich versuchen, echtes LLM-Feedback zu laden (falls verfügbar)
        try {
          await loadInitialFeedback(mockSegments, uploadDataObj);
        } catch (error) {
          console.log('LLM nicht verfügbar, verwende Mock-Daten:', error);
          // Mock-Daten sind bereits geladen
        }
        
        // Initial leere Chat-Messages (werden durch LLM gefüllt)
        const initialMessages = {};
        setChatMessages(initialMessages);
      } else {
        console.warn('Keine Upload-Daten gefunden für LLM Prototype');
      }
    } catch (error) {
      console.error('Error loading data for LLM Prototype:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSegmentClick = (segment) => {
    // Wechsel des aktiven Segments (zeigt den Chat inline)
    setActiveSegment(segment);

    // Audio-Player zum Segment-Start springen lassen
    if (window.audioPlayerRef && window.audioPlayerRef.seekToSegment) {
      window.audioPlayerRef.seekToSegment(segment);
    }
  };

  const closeChat = () => {
    // Schließt den aktiven Chat (inline)
    setActiveSegment(null);
    setCurrentMessage('');
    setIsTyping(false);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !activeSegment) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      message: currentMessage.trim(),
      timestamp: new Date(),
      feedbackType: null
    };

    // Nachricht zu Chat hinzufügen
    setChatMessages(prev => ({
      ...prev,
      [activeSegment.id]: [...(prev[activeSegment.id] || []), userMessage]
    }));

    // Input leeren
    setCurrentMessage('');

    // Typing-Indikator anzeigen
    setIsTyping(true);

    // LLM API Call für Followup-Antwort
    try {
      const assistantMessage = await callLLMApi(activeSegment, currentMessage, 'followup');
      
      setChatMessages(prev => ({
        ...prev,
        [activeSegment.id]: [...(prev[activeSegment.id] || []), assistantMessage]
      }));
      
    } catch (error) {
      console.error('LLM API Error:', error);
      
      // Fallback zu Mock-Antwort bei API-Fehler
      const fallbackMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        message: 'Entschuldigung, ich kann momentan keine detaillierte Antwort generieren. Bitte versuche es später nochmal.',
        timestamp: new Date(),
        feedbackType: activeSegment.feedback
      };

      setChatMessages(prev => ({
        ...prev,
        [activeSegment.id]: [...(prev[activeSegment.id] || []), fallbackMessage]
      }));
    } finally {
      setIsTyping(false);
    }
  };

  // === LLM API Integration Funktionen ===
  
  const checkLLMStatus = async () => {
    try {
      const response = await fetch('/api/llm/status');
      if (response.ok) {
        const status = await response.json();
        setLlmStatus(status);
        
        if (status.testMode) {
          console.log('🧪 LLM Test-Modus aktiv:', status.message);
        } else if (!status.llmAvailable) {
          setLlmError('LLM Service nicht verfügbar');
        }
      }
    } catch (error) {
      console.error('Fehler beim Abrufen des LLM Status:', error);
      setLlmError('LLM Status nicht abrufbar');
    }
  };
  
  const loadInitialFeedback = async (segments, uploadData) => {
    setIsLoadingFeedback(true);
    setLlmError(null);
    
    try {
      const updatedMessages = {};
      
      for (const segment of segments) {
        const initialFeedback = await callLLMApi(segment, null, 'initial', uploadData);
        updatedMessages[segment.id] = [initialFeedback];
      }
      
      setChatMessages(updatedMessages);
    } catch (error) {
      console.error('Error loading initial feedback:', error);
      setLlmError('Fehler beim Laden des initialen Feedbacks. Fallback zu Demo-Modus.');
      // Fallback zu Mock-Daten bei Fehler
      loadMockFeedback(segments);
    } finally {
      setIsLoadingFeedback(false);
    }
  };

  const callLLMApi = async (segment, userMessage = null, type = 'initial', uploadData = null) => {
    const conversationHistory = chatMessages[segment.id] || [];
    
    // User Context aus localStorage/Personalisierung
    const userLanguage = localStorage.getItem('selectedLanguage') || 'Deutsch';
    const useSimpleLanguage = localStorage.getItem('useSimpleLanguage') === 'true';
    const personalMessage = localStorage.getItem('personalMessage') || '';
    
    // Upload Data für Instrumente
    const musicContext = {
      referenceInstrument: uploadData?.referenceInstrument || 'Klavier',
      userInstrument: uploadData?.userInstrument || 'Klavier'
    };
    
    const requestBody = {
      segment: {
        id: segment.id,
        startTime: segment.startTime,
        endTime: segment.endTime,
        feedback: segment.feedback
      },
      musicContext,
      userContext: {
        language: userLanguage,
        simpleLanguage: useSimpleLanguage,
        personalMessage: personalMessage
      },
      conversationHistory: conversationHistory.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.message
      })),
      type: type
    };
    
    // Bei Followup: User-Message hinzufügen
    if (type === 'followup' && userMessage) {
      requestBody.userMessage = userMessage;
    }
    
    const response = await fetch('/api/llm/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'LLM API call failed');
    }
    
    return {
      id: Date.now(),
      sender: 'assistant',
      message: data.response,
      timestamp: new Date(),
      feedbackType: segment.feedback,
      llmGenerated: true
    };
  };

  const loadMockFeedback = (segments) => {
    const mockMessages = {
      1: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Fantastisch! Der Einstieg ist sehr präzise und musikalisch ausgewogen. Die Dynamik ist gut kontrolliert.',
          timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 Minuten früher
          feedbackType: 'good'
        },
        {
          id: 2,
          sender: 'assistant',
          message: 'Hast du Fragen zu diesem Einstieg oder möchtest du etwas Bestimmtes verbessern? 😊',
          timestamp: new Date(Date.now() - 4 * 60 * 1000), // 4 Minuten früher
          feedbackType: 'good'
        }
      ],
      2: [
        {
          id: 1,
          sender: 'assistant', 
          message: 'In diesem Abschnitt sollten wir gezielt arbeiten. Der Rhythmus wird unregelmäßig und die Intonation schwankt. Lass uns das gemeinsam angehen!',
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          feedbackType: 'critical'
        },
        {
          id: 2,
          sender: 'assistant',
          message: 'Keine Sorge, diese Passage ist technisch anspruchsvoll! Was ist dir beim Spielen schwer gefallen?',
          timestamp: new Date(Date.now() - 4 * 60 * 1000),
          feedbackType: 'critical'
        }
      ],
      3: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Hier gibt es sowohl positive als auch verbesserungswürdige Aspekte. Die Melodieführung ist gut, aber achte auf die Artikulation.',
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          feedbackType: 'neutral'
        },
        {
          id: 2,
          sender: 'assistant',
          message: 'Was denkst du denn über diesen mittleren Abschnitt? Hast du beim Spielen etwas Bestimmtes bemerkt?',
          timestamp: new Date(Date.now() - 4 * 60 * 1000),
          feedbackType: 'neutral'
        }
      ],
      4: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Sehr gut! Hier zeigst du wieder eine stabile Technik und gute musikalische Gestaltung. Die Tempoführung ist konstant.',
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          feedbackType: 'good'
        },
        {
          id: 2,
          sender: 'assistant',
          message: 'Dieser Abschnitt gelingt dir bereits sehr gut! Gibt es etwas, womit du besonders zufrieden bist? 😊',
          timestamp: new Date(Date.now() - 4 * 60 * 1000),
          feedbackType: 'good'
        }
      ],
      5: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Der Schluss ist solide, aber es gibt noch Potential für mehr Ausdruck. Die technische Ausführung ist korrekt.',
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          feedbackType: 'neutral'
        },
        {
          id: 2,
          sender: 'assistant',
          message: 'Wie empfindest du denn das Ende des Stücks? Bist du mit dem Schluss zufrieden?',
          timestamp: new Date(Date.now() - 4 * 60 * 1000),
          feedbackType: 'neutral'
        }
      ]
    };
    setChatMessages(mockMessages);
  };

  const generateMockResponse = (userMessage, segment) => {
    const responses = {
      good: [
        'Das ist eine sehr gute Beobachtung! Du zeigst bereits ein gutes Verständnis für die musikalischen Aspekte.',
        'Richtig erkannt! In diesem Segment läuft bereits vieles sehr gut. Weiter so!',
        'Du bist auf dem richtigen Weg! Deine Technik in diesem Bereich ist schon sehr solide.'
      ],
      neutral: [
        'Das ist ein wichtiger Punkt! Lass uns gemeinsam schauen, wie wir das verbessern können.',
        'Gute Frage! Hier können wir definitiv noch etwas optimieren. Hast du schon versucht...?',
        'Du hast einen guten Blick dafür! Dieses Segment bietet tatsächlich Raum für Verbesserungen.'
      ],
      critical: [
        'Danke für deine Frage! Genau solche kritischen Bereiche sind wichtig für deinen Fortschritt.',
        'Das zeigt, dass du aufmerksam zuhörst! Lass uns zusammen eine Strategie entwickeln.',
        'Sehr gut, dass du das ansprichst! Solche Herausforderungen machen dich zu einem besseren Musiker.'
      ]
    };

    const responseArray = responses[segment.feedback] || responses.neutral;
    return responseArray[Math.floor(Math.random() * responseArray.length)];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (isLoading) {
    return (
      <div style={{ 
        height: '100dvh',
        width: '100%', 
        backgroundColor: 'var(--bg-color)', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center' 
      }}>
        <div style={{ textAlign: 'center' }}>
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
          <h3 style={{ color: 'var(--font-color)', margin: '0' }}>
            🎵 LLM Prototyp wird geladen...
          </h3>
          {isLoadingFeedback && (
            <div style={{ marginTop: '10px', fontSize: '14px', color: '#ff9800' }}>
              🤖 Generiere KI-Feedback für Audio-Segmente...
            </div>
          )}
          {llmError && (
            <div style={{ marginTop: '10px', fontSize: '12px', color: '#f44336' }}>
              ⚠️ {llmError}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      height: '100dvh', // Dynamic Viewport Height richtig nutzen
      width: '100%', 
      backgroundColor: 'var(--bg-color)', 
      backgroundImage: 'url(/Rainbow-Line.svg)', 
      backgroundPosition: 'top', 
      backgroundRepeat: 'no-repeat', 
      backgroundSize: 'contain', 
      display: 'flex', 
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden' // Kein Scrollen der ganzen Seite
    }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: 'var(--card-color)', 
        borderRadius: '20px', 
        padding: '20px', 
        margin: '20px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        zIndex: 10,
        flexShrink: 0 // Header behält feste Größe
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {/* Back Button integriert in Header */}
          <button 
            onClick={onBack}
            style={{
              backgroundColor: 'transparent',
              color: 'var(--font-color)',
              border: '2px solid rgba(255,255,255,0.2)',
              padding: '8px 12px',
              borderRadius: '10px',
              cursor: 'pointer',
              fontFamily: "'Nunito', sans-serif",
              fontSize: '14px',
              fontWeight: 'var(--button-font-weight)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            ← Zurück
          </button>
          
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <h1 style={{ 
              margin: '0', 
              color: 'var(--font-color)', 
              fontSize: 'clamp(16px, 4vw, 24px)'
            }}>
              🤖 LLM Feedback Prototyp
            </h1>
            {(llmStatus?.testMode || llmError) && (
              <div style={{ 
                fontSize: '12px', 
                color: llmStatus?.testMode ? '#ff9800' : '#f44336', 
                marginTop: '5px',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}>
                {llmStatus?.testMode ? '🧪 Test-Modus' : '⚠️ Demo-Modus'} 
                {llmStatus?.message && ` - ${llmStatus.message.replace(/🧪|🤖|⚠️/g, '').trim()}`}
              </div>
            )}
          </div>
        </div>
        <img src="/MuDiKo_Logo.svg" alt="MuDiKo Logo" style={{ 
          width: 'clamp(45px, 8vw, 60px)', // Responsive Logo
          height: 'clamp(45px, 8vw, 60px)' 
        }} />
      </div>

      {/* Main Content Area */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between', // Chat oben, Player unten
        position: 'relative',
        padding: '0', // Kein Padding - wir verwenden Margin für Alignment
        paddingBottom: '0px', // Kein Padding unten
        overflow: 'hidden' // Verhindert Scrollen
      }}>
        
        {/* Chat Area - am oberen Rand */}
        {activeSegment && (
          <div style={{
            backgroundColor: 'var(--card-color)',
            borderRadius: '20px',
            padding: '20px',
            margin: '0 20px 20px 20px', // Gleiche Margins wie Header
            height: 'calc(100dvh - 300px)', // DVH richtig nutzen, Platz für Header und Player
            boxShadow: 'var(--shadow)',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px',
            overflow: 'hidden' // Chat soll intern scrollen
          }}>
            {/* Chat Header - vereinfacht ohne Close Button */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'flex-start', 
              alignItems: 'center', 
              paddingBottom: '15px',
              borderBottom: '1px solid rgba(255,255,255,0.1)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ 
                  width: '40px', 
                  height: '40px', 
                  borderRadius: '12px', 
                  backgroundColor: activeSegment.color, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontSize: '20px' 
                }}>
                  {activeSegment.emoji}
                </div>
                <div>
                  <div style={{ color: 'var(--font-color)', fontWeight: 'var(--button-font-weight)', fontSize: '18px' }}>
                    Segment {activeSegment.id}
                  </div>
                  <div style={{ fontSize: '14px', color: activeSegment.color, fontWeight: '600' }}>
                    {activeSegment.feedback === 'good' ? 'Positives Feedback' : 
                     activeSegment.feedback === 'neutral' ? 'Neutrales Feedback' : 
                     'Verbesserungsvorschläge'}
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div ref={chatMessagesRef} style={{ 
              flex: 1, // Nimmt verfügbaren Platz
              overflow: 'auto', 
              padding: '0px', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '16px'
            }}>
              {(chatMessages[activeSegment.id] || []).map(msg => (
                <div key={msg.id} style={{ 
                  display: 'flex', 
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  padding: '0 10px' // Mehr Abstand zu den Seiten
                }}>
                  <div style={{ 
                    maxWidth: '85%', // Breiter für bessere Lesbarkeit
                    position: 'relative',
                    paddingLeft: msg.sender === 'assistant' ? '15px' : '0px',
                    paddingRight: msg.sender === 'user' ? '15px' : '0px'
                  }}>
                    {/* Vertikale Farbline am Rand */}
                    <div style={{
                      position: 'absolute',
                      left: msg.sender === 'user' ? 'auto' : '0px',
                      right: msg.sender === 'user' ? '0px' : 'auto',
                      top: 0,
                      bottom: 0,
                      width: '4px',
                      backgroundColor: msg.sender === 'assistant' ? activeSegment.color : 'var(--mudiko-pink)',
                      borderRadius: '2px',
                      opacity: 0.8
                    }} />
                    
                    {/* Name über der Nachricht */}
                    <div style={{ 
                      fontSize: '12px', 
                      color: msg.sender === 'assistant' ? activeSegment.color : 'var(--mudiko-pink)', 
                      marginBottom: '6px', 
                      fontWeight: '600',
                      textAlign: msg.sender === 'user' ? 'right' : 'left'
                    }}>
                      {msg.sender === 'assistant' ? '🤖 KI-Assistent' : '👤 Schüler'}
                    </div>
                    
                    {/* Nachricht */}
                    <div style={{ 
                      backgroundColor: 'var(--button-color)', 
                      color: 'var(--font-color)', 
                      padding: '12px 16px', 
                      borderRadius: msg.sender === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      border: `2px solid ${msg.sender === 'assistant' ? activeSegment.color + '40' : 'var(--mudiko-pink)40'}`,
                      boxShadow: 'var(--shadow)'
                    }}>
                      <div style={{ fontSize: '14px', lineHeight: '1.4' }}>{msg.message}</div>
                      <div style={{ 
                        fontSize: '10px', 
                        color: 'rgba(255,255,255,0.5)', 
                        marginTop: '8px', 
                        textAlign: 'right' 
                      }}>
                        {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div style={{ 
              display: 'flex', 
              gap: '12px', 
              alignItems: 'center', 
              paddingTop: '15px',
              borderTop: '1px solid rgba(255,255,255,0.1)',
              flexShrink: 0 // Input behält feste Größe
            }}>
              <input 
                value={currentMessage} 
                onChange={(e) => setCurrentMessage(e.target.value)} 
                onKeyPress={handleKeyPress} 
                placeholder={`Frage an Segment ${activeSegment.id}...`} 
                style={{ 
                  flex: 1, 
                  padding: '12px 16px', 
                  borderRadius: '10px', 
                  border: '2px solid rgba(255,255,255,0.1)', 
                  background: 'var(--button-color)', 
                  color: 'var(--font-color)',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: "'Nunito', sans-serif"
                }} 
              />
              <button 
                onClick={sendMessage} 
                disabled={!currentMessage.trim()} 
                style={{ 
                  backgroundColor: '#666666', // Grauer Hintergrund
                  color: 'white', // Weißer Text
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '10px',
                  cursor: currentMessage.trim() ? 'pointer' : 'not-allowed',
                  fontFamily: "'Nunito', sans-serif",
                  fontSize: '14px',
                  fontWeight: 'var(--button-font-weight)',
                  boxShadow: 'var(--shadow)',
                  opacity: currentMessage.trim() ? 1 : 0.5,
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  if (currentMessage.trim()) {
                    e.target.style.backgroundColor = '#555555';
                  }
                }}
                onMouseLeave={(e) => {
                  if (currentMessage.trim()) {
                    e.target.style.backgroundColor = '#666666';
                  }
                }}
              >
                {isTyping ? '...' : 'Senden'}
              </button>
            </div>
          </div>
        )}

        {/* Audio Player mit integrierten Segment Buttons - am unteren Rand */}
        <div style={{
          flexShrink: 0, // Behält feste Größe
          backgroundColor: 'var(--card-color)',
          borderRadius: '20px', // Vollständig abgerundet wie Header
          padding: '20px',
          margin: '0 20px 20px 20px', // Gleiche Margins wie Header und Chat
          boxShadow: 'var(--shadow)'
        }}>
          {/* Audio Player mit integrierten Segment Buttons */}
          <div style={{ 
            width: '100%'
          }}>
            <AudioPlayer 
              uploadData={uploadData} 
              segments={segments}
              activeSegment={activeSegment}
              currentSegment={currentSegment}
              onSegmentClick={handleSegmentClick}
              onTimeUpdate={(currentTime) => {
                // Bestimme aktuelles Segment basierend auf Audio-Zeit
                const current = segments.find(segment => 
                  currentTime >= segment.startTime && currentTime < segment.endTime
                );
                setCurrentSegment(current);
              }}
            />
          </div>
        </div>
      </div>

      {/* CSS Animation für Loading Spinner, Pulse und Typing */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(1.2); }
          100% { opacity: 1; transform: scale(1); }
        }
        @keyframes typingDot {
          0%, 60%, 100% { 
            transform: translateY(0);
            opacity: 0.4;
          }
          30% { 
            transform: translateY(-10px);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
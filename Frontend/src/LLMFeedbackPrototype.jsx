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
  const [showGeneralChat, setShowGeneralChat] = useState(false); // Allgemeiner Chat
  const chatMessagesRef = useRef(null);

    // Auto-scroll zu neuesten Nachrichten
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages, activeSegment]);

  // Hilfsfunktion für Chat-Emoji basierend auf feedbackType
  const getChatEmoji = (feedbackType) => {
    switch (feedbackType) {
      case 'good':
        return '/Emoji_grün_positiv_chat.svg';
      case 'critical':
        return '/Emoji_rot_negativ_chat.svg';
      case 'neutral':
        return '/Emoji_orange_neutral_chat.svg';
      default:
        return '/Emoji_orange_neutral_chat.svg';
    }
  };

  // Hilfsfunktion für normale Emojis (ohne _chat) für Segment-Buttons
  const getSegmentEmoji = (feedbackType) => {
    switch (feedbackType) {
      case 'good':
        return '/Emoji_grün_positiv.svg';
      case 'critical':
        return '/Emoji_rot_negativ.svg';
      case 'neutral':
        return '/Emoji_orange_neutral.svg';
      default:
        return '/Emoji_orange_neutral.svg';
    }
  };

  // Hilfsfunktion für Zeitformatierung
  const formatSegmentTime = (startTime, endTime) => {
    const duration = endTime - startTime;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    const startMin = Math.floor(startTime / 60);
    const startSec = Math.floor(startTime % 60);
    const endMin = Math.floor(endTime / 60);
    const endEndSec = Math.floor(endTime % 60);
    
    return {
      duration: `${minutes}:${seconds.toString().padStart(2, '0')}`,
      timeRange: `${startMin}:${startSec.toString().padStart(2, '0')} - ${endMin}:${endEndSec.toString().padStart(2, '0')}`
    };
  };

  // Load saved data on component mount
  useEffect(() => {
    initializeData();
  }, []);

  // Auto-open ersten Segment Chat beim Start
  useEffect(() => {
    if (segments.length > 0 && !activeSegment && !showGeneralChat) {
      setShowGeneralChat(true); // Starte mit allgemeinem Chat
    }
  }, [segments, activeSegment, showGeneralChat]);

  // Reset isTyping beim Wechsel des aktiven Segments
  useEffect(() => {
    setIsTyping(false);
    setCurrentMessage('');
  }, [activeSegment, showGeneralChat]);

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
          { id: 1, startTime: 0, endTime: 8, feedback: 'good', emoji: '/Emoji_grün_positiv_chat.svg', segmentEmoji: '/Emoji_grün_positiv.svg', color: '#4CAF50', bgColor: '#EDF8F0' },
          { id: 2, startTime: 8, endTime: 16, feedback: 'neutral', emoji: '/Emoji_orange_neutral_chat.svg', segmentEmoji: '/Emoji_orange_neutral.svg', color: '#FF9800', bgColor: '#FFF3E6' },
          { id: 3, startTime: 16, endTime: 24, feedback: 'neutral', emoji: '/Emoji_orange_neutral_chat.svg', segmentEmoji: '/Emoji_orange_neutral.svg', color: '#FF9800', bgColor: '#FFF3E6' },
          { id: 4, startTime: 24, endTime: 32, feedback: 'critical', emoji: '/Emoji_rot_negativ_chat.svg', segmentEmoji: '/Emoji_rot_negativ.svg', color: '#F44336', bgColor: '#F9EBEB' },
          { id: 5, startTime: 32, endTime: 40, feedback: 'critical', emoji: '/Emoji_rot_negativ_chat.svg', segmentEmoji: '/Emoji_rot_negativ.svg', color: '#F44336', bgColor: '#F9EBEB' }
        ];
        setSegments(mockSegments);

        // Initiales LLM Feedback für jedes Segment laden
        // Erst Mock-Daten laden (sofort verfügbar)
        const mockMessages = generateMockMessages(mockSegments);
        setChatMessages(mockMessages);
        
        // Zusätzlich versuchen, echtes LLM-Feedback zu laden (falls verfügbar)
        try {
          await loadInitialFeedback(mockSegments, uploadDataObj);
        } catch (error) {
          console.log('LLM nicht verfügbar, verwende Mock-Daten:', error);
          // Mock-Daten sind bereits geladen
        }
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
    if (!currentMessage.trim() || (!activeSegment && !showGeneralChat)) return;

    const chatId = showGeneralChat ? 'general' : activeSegment.id;

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
      [chatId]: [...(prev[chatId] || []), userMessage]
    }));

    // Input leeren
    setCurrentMessage('');

    // Typing-Indikator anzeigen
    setIsTyping(true);

    // Simulierte Typing-Verzögerung (1-2 Sekunden)
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    // LLM API Call für Followup-Antwort
    try {
      const assistantMessage = showGeneralChat 
        ? await callLLMApi(null, currentMessage, 'general')
        : await callLLMApi(activeSegment, currentMessage, 'followup');
      
      setIsTyping(false);
      
      setChatMessages(prev => ({
        ...prev,
        [chatId]: [...(prev[chatId] || []), assistantMessage]
      }));
      
    } catch (error) {
      console.error('LLM API Error:', error);
      
      setIsTyping(false);
      
      // Fallback zu Mock-Antwort bei API-Fehler
      const fallbackMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        message: 'Entschuldigung, ich kann momentan keine detaillierte Antwort generieren. Bitte versuche es später nochmal.',
        timestamp: new Date(),
        feedbackType: showGeneralChat ? 'neutral' : activeSegment.feedback
      };

      setChatMessages(prev => ({
        ...prev,
        [chatId]: [...(prev[chatId] || []), fallbackMessage]
      }));
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
    const mockMessages = generateMockMessages(segments);
    // Nachrichten direkt setzen ohne Animation beim initialen Laden aller Segmente
    setChatMessages(mockMessages);
  };

  const generateMockMessages = (segments) => {
    const mockMessages = {
      1: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Du hast hier die gleichen Akkorde und die richtige Tonart (F-Dur) wie die Lehrkraft verwendet. Super! Dein Klang ist etwas heller und lauter, was Kraft zeigt. Versuch beim nächsten Mal, die Lautstärke etwas gleichmäßiger zu halten, damit es ruhiger wirkt.',
          timestamp: new Date(),
          feedbackType: 'good'
        }
      ],
      2: [
        {
          id: 1,
          sender: 'assistant', 
          message: 'Du hast das Tempo leicht verlangsamt und einige kleine Pausen eingebaut. Das Stück klingt dadurch etwas zögerlich. Übe, die Töne fließender aneinanderzureihen – zähle innerlich mit, um im Rhythmus zu bleiben.',
          timestamp: new Date(),
          feedbackType: 'neutral'
        }
      ],
      3: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Die Akkorde stimmen weiterhin, sehr gut! Allerdings sind manche Töne etwas zu hoch und du machst zusätzliche Pausen. Spiele die Passage einmal mit der Referenzaufnahme zusammen – das hilft dir, die Töne besser abzustimmen.',
          timestamp: new Date(),
          feedbackType: 'neutral'
        }
      ],
      4: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Hier hast du zwar dieselben Akkorde, aber dein Klang ist deutlich heller und das Spiel etwas unruhig. Vermutlich warst du an dieser Stelle etwas zu schnell. Versuch, gleichmäßig zu bleiben und die Töne sanfter anzuschlagen.',
          timestamp: new Date(),
          feedbackType: 'critical'
        }
      ],
      5: [
        {
          id: 1,
          sender: 'assistant',
          message: 'In diesem Abschnitt sind die Töne deutlich höher und unregelmäßiger. Auch die Lautstärke schwankt stark. Übe diese Stelle in kleinen Abschnitten – lieber langsam und sicher, bevor du das Tempo wieder erhöhst.',
          timestamp: new Date(),
          feedbackType: 'critical'
        }
      ],
      general: [
        {
          id: 1,
          sender: 'assistant',
          message: 'Hallo! Ich bin dein Musik-KI-Assistent und habe deine Aufnahme sorgfältig mit der Referenzaufnahme deiner Lehrkraft verglichen. Ich möchte dir ein ehrliches und hilfreiches Feedback geben, damit du genau weißt, was du schon gut machst – und wo du dich noch verbessern kannst.\n\n🌟 Lob\n\nDu hast dich hörbar bemüht, das Stück nachzuspielen und dich an der Tonart sowie den Akkorden der Lehrkraft orientiert. Besonders schön ist, dass du die Harmonien in allen Segmenten gut getroffen hast – die Grundakkorde stimmen meist mit der Vorlage überein!\n\nAuch dein Tempo ist über weite Strecken recht konstant, was zeigt, dass du den musikalischen Fluss schon gut im Gefühl hast.\n\n⚠️ Fehleranalyse\n\nIn mehreren Abschnitten fällt auf, dass deine Töne oft höher klingen als in der Referenz – also leicht „überzogen" in der Tonhöhe.\n\nAußerdem sind die Lautstärken manchmal sehr unterschiedlich, wodurch dein Vortrag etwas unruhig wirkt. Auch deine Dynamik (also die Unterschiede zwischen laut und leise) ist stärker ausgeprägt als bei der Lehrkraft. Das ist grundsätzlich gut, aber manchmal übertreibst du es ein wenig, wodurch der Zusammenhang zwischen den einzelnen Phrasen verloren geht.\n\nGelegentlich machst du kleine Pausen oder Stopps, die im Original nicht vorkommen – vielleicht hast du an diesen Stellen kurz gezögert oder geatmet. Das ist normal, aber übe, die Übergänge flüssiger zu gestalten.\n\n💡 Tipps zur Verbesserung\n\n• Achte auf gleichmäßigere Lautstärke. Übe das Stück einmal sehr langsam und konzentriere dich darauf, dass alle Töne etwa gleich stark klingen.\n\n• Tonhöhe kontrollieren: Spiele (oder singe) jeden Abschnitt mit einem Stimmgerät oder Klavier als Orientierung, um sicherzugehen, dass du die richtigen Töne triffst.\n\n• Pausen vermeiden: Versuche, durchzuspielen, auch wenn dir ein kleiner Fehler passiert – das hilft, das Gefühl für den musikalischen Fluss zu behalten.\n\n• Dynamik üben: Spiele dieselbe Passage einmal „ruhiger" und einmal „ausdrucksstärker". So lernst du besser, wie du die Lautstärke gezielt einsetzt.\n\n🪶 Zusammenfassung\n\nDu bist auf einem guten Weg! Du kennst die Harmonien und hast ein Gespür für Rhythmus und Ausdruck.\n\nArbeite jetzt daran, dein Spiel gleichmäßiger und sicherer zu gestalten. Achte vor allem auf Tonhöhe und Lautstärke.\n\nWenn du magst, kann ich dir beim nächsten Üben gezielte Übungen oder Playbacks zum Mitspielen vorschlagen, die genau zu deinem aktuellen Stand passen.',
          timestamp: new Date(),
          feedbackType: 'neutral'
        }
      ]
    };
    return mockMessages;
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
          <h3 style={{ color: 'white', margin: '0' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flex: 1 }}>
          {/* Back Button integriert in Header */}
          <button 
            onClick={onBack}
            style={{
              backgroundColor: 'transparent',
              color: 'white',
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
          
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
            <h1 style={{ 
              margin: '0', 
              color: 'white', 
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
          
          {/* Dateiname */}
          {uploadData?.original_filenames?.schueler && (
            <div style={{
              fontSize: '14px',
              color: 'white',
              backgroundColor: 'rgba(255,255,255,0.1)',
              padding: '6px 12px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              border: '1px solid rgba(255,255,255,0.2)'
            }}>
              🎵 {uploadData.original_filenames.schueler}
            </div>
          )}
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
        <div style={{
          backgroundColor: 'var(--card-color)',
          borderRadius: '20px',
          padding: '0',
          margin: '0 20px 20px 20px', // Gleiche Margins wie Header
          height: 'calc(100dvh - 300px)', // DVH richtig nutzen, Platz für Header und Player
          boxShadow: 'var(--shadow)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden' // Chat soll intern scrollen
        }}>
          {/* Chat Tabs - Browser-Style */}
          <div style={{
            display: 'flex',
            gap: '4px',
            padding: '8px 8px 0 8px',
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: '20px 20px 0 0',
            overflowX: 'auto',
            flexShrink: 0
          }}>
            {/* Allgemeiner Chat Tab */}
            <button
              onClick={() => {
                setShowGeneralChat(true);
                setActiveSegment(null);
              }}
              style={{
                backgroundColor: showGeneralChat ? 'var(--card-color)' : 'transparent',
                color: 'white',
                border: 'none',
                padding: '10px 16px',
                borderRadius: '10px 10px 0 0',
                cursor: 'pointer',
                fontFamily: "'Nunito', sans-serif",
                fontSize: '14px',
                fontWeight: 'var(--button-font-weight)',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                whiteSpace: 'nowrap',
                borderBottom: showGeneralChat ? '3px solid var(--mudiko-pink)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (!showGeneralChat) {
                  e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (!showGeneralChat) {
                  e.target.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>💬</span>
              <span>Allgemein</span>
            </button>

            {/* Segment Tabs */}
            {segments.map((segment) => {
              const isActive = activeSegment && activeSegment.id === segment.id;
              return (
                <button
                  key={segment.id}
                  onClick={() => {
                    setActiveSegment(segment);
                    setShowGeneralChat(false);
                  }}
                  style={{
                    backgroundColor: isActive ? 'var(--card-color)' : 'transparent',
                    color: 'white',
                    border: 'none',
                    padding: '10px 16px',
                    borderRadius: '10px 10px 0 0',
                    cursor: 'pointer',
                    fontFamily: "'Nunito', sans-serif",
                    fontSize: '14px',
                    fontWeight: 'var(--button-font-weight)',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    whiteSpace: 'nowrap',
                    borderBottom: isActive ? `3px solid ${segment.color}` : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.target.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <img 
                    src={getChatEmoji(segment.feedback)} 
                    alt={`${segment.feedback} emoji`}
                    style={{
                      width: '20px',
                      height: '20px'
                    }}
                  />
                  <span>Segment {segment.id}</span>
                </button>
              );
            })}
          </div>

          {/* Chat Content */}
          <div style={{
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px',
            flex: 1,
            overflow: 'hidden'
          }}>

            {/* Chat Messages */}
            <div ref={chatMessagesRef} style={{ 
              flex: 1, // Nimmt verfügbaren Platz
              overflow: 'auto', 
              padding: '0px', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '16px'
            }}>
              {(chatMessages[showGeneralChat ? 'general' : activeSegment?.id] || []).map(msg => {
                const segmentColor = showGeneralChat ? '#FF9800' : activeSegment?.color;
                return (
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
                        backgroundColor: msg.sender === 'assistant' ? segmentColor : 'var(--mudiko-pink)',
                        borderRadius: '2px',
                        opacity: 0.8
                      }} />
                      
                      {/* Name über der Nachricht */}
                      <div style={{ 
                        fontSize: '12px', 
                        color: msg.sender === 'assistant' ? segmentColor : 'var(--mudiko-pink)', 
                        marginBottom: '6px', 
                        fontWeight: '600',
                        textAlign: msg.sender === 'user' ? 'right' : 'left',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start'
                      }}>
                        {msg.sender === 'assistant' && msg.feedbackType && !showGeneralChat && (
                          <img 
                            src={getChatEmoji(msg.feedbackType)} 
                            alt={`${msg.feedbackType} feedback`}
                            style={{ 
                              width: '20px', 
                              height: '20px',
                              borderRadius: '50%',
                              backgroundColor: 'rgba(255,255,255,0.1)',
                              padding: '2px'
                            }} 
                          />
                        )}
                        {msg.sender === 'assistant' ? 'KI-Assistent' : '👤 Schüler'}
                      </div>
                      
                      {/* Nachricht */}
                      <div style={{ 
                        backgroundColor: 'var(--button-color)', 
                        color: 'white', 
                        padding: '12px 16px', 
                        borderRadius: msg.sender === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                        border: `2px solid ${msg.sender === 'assistant' ? segmentColor + '40' : 'var(--mudiko-pink)40'}`,
                        boxShadow: 'var(--shadow)'
                      }}>
                        <div style={{ fontSize: '14px', lineHeight: '1.4' }}>{msg.message}</div>
                        <div style={{ 
                          fontSize: '10px', 
                          color: 'white', 
                          marginTop: '8px', 
                          textAlign: 'right' 
                        }}>
                          {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'flex-start',
                  padding: '0 10px'
                }}>
                  <div style={{ 
                    position: 'relative',
                    paddingLeft: '15px'
                  }}>
                    {/* Vertikale Farbline am Rand */}
                    <div style={{
                      position: 'absolute',
                      left: '0px',
                      top: 0,
                      bottom: 0,
                      width: '4px',
                      backgroundColor: showGeneralChat ? '#FF9800' : activeSegment?.color,
                      borderRadius: '2px',
                      opacity: 0.8
                    }} />
                    
                    {/* Name über der Typing-Bubble */}
                    <div style={{ 
                      fontSize: '12px', 
                      color: showGeneralChat ? '#FF9800' : activeSegment?.color, 
                      marginBottom: '6px', 
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      {!showGeneralChat && activeSegment?.feedbackType && (
                        <img 
                          src={getChatEmoji(activeSegment.feedback)} 
                          alt="typing"
                          style={{ 
                            width: '20px', 
                            height: '20px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(255,255,255,0.1)',
                            padding: '2px'
                          }} 
                        />
                      )}
                      KI-Assistent
                    </div>
                    
                    {/* Typing Bubble */}
                    <div style={{ 
                      backgroundColor: 'var(--button-color)', 
                      padding: '12px 16px', 
                      borderRadius: '16px 16px 16px 4px',
                      border: `2px solid ${showGeneralChat ? '#FF9800' : activeSegment?.color}40`,
                      boxShadow: 'var(--shadow)',
                      display: 'flex',
                      gap: '6px',
                      alignItems: 'center'
                    }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: showGeneralChat ? '#FF9800' : activeSegment?.color,
                        animation: 'typingDot 1.4s infinite ease-in-out',
                        animationDelay: '0s'
                      }} />
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: showGeneralChat ? '#FF9800' : activeSegment?.color,
                        animation: 'typingDot 1.4s infinite ease-in-out',
                        animationDelay: '0.2s'
                      }} />
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: showGeneralChat ? '#FF9800' : activeSegment?.color,
                        animation: 'typingDot 1.4s infinite ease-in-out',
                        animationDelay: '0.4s'
                      }} />
                    </div>
                  </div>
                </div>
              )}
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
                placeholder={showGeneralChat ? 'Deine Frage...' : `Frage an Segment ${activeSegment?.id}...`} 
                style={{ 
                  flex: 1, 
                  padding: '12px 16px', 
                  borderRadius: '10px', 
                  border: '2px solid rgba(255,255,255,0.1)', 
                  background: 'var(--button-color)', 
                  color: 'white',
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
        </div>

        {/* Audio Player direkt ohne Container */}
        <div style={{
          flexShrink: 0, // Behält feste Größe
          margin: '0 20px 20px 20px' // Gleiche Margins wie Header und Chat
        }}>
          <AudioPlayer 
            uploadData={uploadData} 
            segments={segments}
            activeSegment={activeSegment}
            currentSegment={currentSegment}
            onSegmentClick={(segment) => {
              setActiveSegment(segment);
              setShowGeneralChat(false);
            }}
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
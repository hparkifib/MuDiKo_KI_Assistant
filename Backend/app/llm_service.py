"""
LLM API Integration für MuDiKo KI-Assistent
Unterstützt OpenAI GPT und Anthropic Claude APIs
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import asyncio

# Konfiguration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # 'openai' oder 'anthropic'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')  # oder 'claude-3-haiku-20240307'

# Test-Mode Konfiguration
TEST_MODE = os.getenv('LLM_TEST_MODE', 'auto').lower()  # 'auto', 'force', 'disabled'

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAPIError(Exception):
    """Custom Exception für LLM API Fehler"""
    pass

class LLMService:
    """Service für LLM API Kommunikation"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.model = LLM_MODEL
        self.test_mode = self._determine_test_mode()
        
        # Debug: API Keys prüfen
        has_keys = self._has_api_keys()
        logger.info(f"🔍 DEBUG - Valid API Keys: {has_keys}, Provider: {self.provider}, Test-Mode: {self.test_mode}")
        
        # Test-Mode Status loggen
        if self.test_mode:
            logger.info("🧪 LLM TEST-MODUS AKTIV - Verwende Mock-Responses für Entwicklung")
        else:
            logger.info(f"🤖 LLM PRODUKTIV-MODUS - Provider: {self.provider}, Model: {self.model}")
        
        # API Keys validieren
        if self.provider == 'openai' and not OPENAI_API_KEY and not self.test_mode:
            logger.warning("OPENAI_API_KEY nicht gesetzt - Fallback zu Test-Modus")
        elif self.provider == 'anthropic' and not ANTHROPIC_API_KEY and not self.test_mode:
            logger.warning("ANTHROPIC_API_KEY nicht gesetzt - Fallback zu Test-Modus")
    
    async def generate_response(self, 
                              prompt: str, 
                              max_tokens: int = 500,
                              temperature: float = 0.7) -> str:
        """
        Generiert LLM Response basierend auf Prompt
        
        Args:
            prompt: Vollständiger Prompt für das LLM
            max_tokens: Maximale Anzahl Tokens in der Antwort
            temperature: Kreativität (0.0 = deterministisch, 1.0 = sehr kreativ)
            
        Returns:
            str: Generierte Antwort vom LLM
            
        Raises:
            LLMAPIError: Bei API-Fehlern
        """
        
        if not self._api_available():
            return self._generate_fallback_response()
        
        try:
            if self.provider == 'openai':
                return await self._call_openai_api(prompt, max_tokens, temperature)
            elif self.provider == 'anthropic':
                return await self._call_anthropic_api(prompt, max_tokens, temperature)
            else:
                raise LLMAPIError(f"Unbekannter LLM Provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM API Error: {str(e)}")
            return self._generate_fallback_response()
    
    async def _call_openai_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """OpenAI API Call"""
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise LLMAPIError(f"OpenAI API Error {response.status}: {error_text}")
                
                result = await response.json()
                
                if 'choices' not in result or len(result['choices']) == 0:
                    raise LLMAPIError("Keine Antwort von OpenAI API erhalten")
                
                return result['choices'][0]['message']['content'].strip()
    
    async def _call_anthropic_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Anthropic Claude API Call"""
        
        headers = {
            'x-api-key': ANTHROPIC_API_KEY,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise LLMAPIError(f"Anthropic API Error {response.status}: {error_text}")
                
                result = await response.json()
                
                if 'content' not in result or len(result['content']) == 0:
                    raise LLMAPIError("Keine Antwort von Anthropic API erhalten")
                
                return result['content'][0]['text'].strip()
    
    def _determine_test_mode(self) -> bool:
        """Bestimmt ob Test-Modus aktiv sein soll"""
        if TEST_MODE == 'force':
            return True
        elif TEST_MODE == 'disabled':
            return False
        else:  # 'auto'
            # Auto-Mode: Test-Modus wenn keine API Keys verfügbar
            return not self._has_api_keys()
    
    def _has_api_keys(self) -> bool:
        """Prüft ob API Keys verfügbar sind"""
        if self.provider == 'openai':
            # Prüfe ob Key gesetzt und nicht ein Beispiel-Key ist
            return bool(OPENAI_API_KEY and 
                       OPENAI_API_KEY.strip() and 
                       not OPENAI_API_KEY.startswith('sk-proj-your') and
                       OPENAI_API_KEY != 'your_openai_api_key_here')
        elif self.provider == 'anthropic':
            # Prüfe ob Key gesetzt und nicht ein Beispiel-Key ist  
            return bool(ANTHROPIC_API_KEY and 
                       ANTHROPIC_API_KEY.strip() and 
                       not ANTHROPIC_API_KEY.startswith('sk-ant-your') and
                       ANTHROPIC_API_KEY != 'your_anthropic_api_key_here')
        return False
    
    def _api_available(self) -> bool:
        """Prüft ob LLM API verfügbar ist"""
        if self.test_mode:
            return False  # In Test-Mode verwende immer Mock-Responses
        return self._has_api_keys()
    
    def _generate_fallback_response(self) -> str:
        """Fallback Response - unterscheidet zwischen Test-Mode und echten Fehlern"""
        if self.test_mode:
            # Test-Mode: Realistische Demo-Responses
            test_responses = [
                "🧪 [TEST-MODUS] Fantastisch! In diesem Segment zeigst du schon eine sehr gute Kontrolle über Rhythmus und Dynamik. Deine Phrasierung ist ausdrucksvoll und musikalisch durchdacht.",
                "🧪 [TEST-MODUS] Hier sehe ich sowohl Stärken als auch Verbesserungspotential. Die Grundtechnik stimmt, aber wir könnten noch an der Präzision arbeiten. Was denkst du selbst über diesen Abschnitt?",
                "🧪 [TEST-MODUS] Das ist ein wichtiger Lernbereich! Hier können wir gemeinsam viel erreichen. Lass uns gezielt an der Intonation und dem Timing arbeiten. Hast du Fragen zu diesem Teil?"
            ]
        else:
            # Echter Fehler: Höfliche Fehlermeldungen
            test_responses = [
                "Entschuldigung, ich kann momentan keine personalisierte Antwort generieren. Die KI-Funktionen sind temporär nicht verfügbar. Bitte versuche es später erneut.",
                "Die KI-Analyse ist gerade nicht verfügbar. Du kannst aber gerne deine Fragen stellen - ich werde versuchen, dir bestmöglich zu helfen, sobald die Verbindung wieder hergestellt ist.",
                "Aktuell kann ich keine detaillierte Analyse durchführen. Die KI-Services sind momentan nicht erreichbar. Deine Aufnahme wurde aber gespeichert und du kannst später nochmal nachfragen."
            ]
        
        import random
        return random.choice(test_responses)

# Globaler LLM Service
llm_service = LLMService()

# Flask Route Integration
from flask import request, jsonify
from llm_prompt_system import LLMPromptSystem

# Globaler Prompt System
prompt_system = LLMPromptSystem()

async def handle_llm_feedback_request(request_data: Dict) -> Dict:
    """
    Hauptfunktion für LLM Feedback Requests
    
    Args:
        request_data: Dictionary mit allen notwendigen Daten
        
    Returns:
        Dict mit generierter Antwort und Metadaten
    """
    
    try:
        # Request-Daten extrahieren
        segment_data = request_data.get('segment', {})
        music_context = request_data.get('musicContext', {})
        user_context = request_data.get('userContext', {})
        conversation_history = request_data.get('conversationHistory', [])
        user_message = request_data.get('userMessage', '')
        feedback_type = request_data.get('type', 'initial')  # 'initial' oder 'followup'
        
        # Validierung
        if not segment_data:
            raise ValueError("Segment-Daten fehlen")
        
        # Prompt generieren
        if feedback_type == 'initial':
            prompt = prompt_system.generate_initial_feedback_prompt(
                segment_data, music_context, user_context
            )
        else:  # followup
            if not user_message:
                raise ValueError("User-Message fehlt für Followup")
            
            prompt = prompt_system.generate_followup_prompt(
                segment_data, music_context, user_context, 
                conversation_history, user_message
            )
        
        # LLM API Call
        response = await llm_service.generate_response(
            prompt=prompt,
            max_tokens=300,  # Kompakte Antworten für Chat
            temperature=0.7
        )
        
        # Response formatieren
        result = {
            'success': True,
            'response': response,
            'segmentId': segment_data.get('id'),
            'feedbackType': segment_data.get('feedback', 'neutral'),
            'timestamp': datetime.now().isoformat(),
            'llmProvider': llm_service.provider if not llm_service.test_mode else 'test-mode',
            'llmModel': llm_service.model if not llm_service.test_mode else 'mock-responses',
            'testMode': llm_service.test_mode
        }
        
        logger.info(f"LLM Feedback generiert für Segment {segment_data.get('id')}")
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_llm_feedback_request: {str(e)}")
        
        # Fallback Response
        return {
            'success': False,
            'error': str(e),
            'response': llm_service._generate_fallback_response(),
            'timestamp': datetime.now().isoformat()
        }

# Mock-Daten für Entwicklung (wenn LLM APIs nicht verfügbar)
def get_mock_response(segment_data: Dict, user_message: str = None) -> str:
    """Generiert Mock-Responses für Entwicklung"""
    
    feedback_type = segment_data.get('feedback', 'neutral')
    segment_id = segment_data.get('id', 1)
    
    if user_message:  # Followup Response
        responses = {
            'good': [
                f"Das ist eine super Beobachtung zu Segment {segment_id}! Du zeigst wirklich gutes musikalisches Verständnis.",
                f"Genau richtig erkannt! In diesem Bereich läuft schon vieles sehr gut bei dir.",
                f"Du hörst sehr aufmerksam! Das ist ein Zeichen dafür, dass du musikalisch wächst."
            ],
            'neutral': [
                f"Gute Frage zu Segment {segment_id}! Hier können wir definitiv noch verfeinern.",
                f"Das ist ein wichtiger Punkt! Lass uns gemeinsam schauen, wie wir das optimieren können.",
                f"Du hast einen guten Blick für Details! Hier gibt es tatsächlich Raum für Verbesserung."
            ],
            'critical': [
                f"Sehr gut, dass du das ansprichst! Genau solche Fragen helfen dir beim Weiterkommen.",
                f"Das zeigt, dass du aufmerksam übst! Lass uns eine Strategie für diesen Bereich entwickeln.",
                f"Perfekte Frage! Solche Herausforderungen sind normal und wichtig für deinen Fortschritt."
            ]
        }
    else:  # Initial Response
        responses = {
            'good': [
                f"Hervorragend! Dein Spiel in diesem Segment zeigt schon viel musikalisches Gefühl. Besonders die Rhythmuspräzision gefällt mir.",
                f"Wirklich gut gemacht! Die Dynamik und der Klang stimmen hier bereits sehr gut. Hast du Fragen dazu?",
                f"Starke Leistung! Deine Technik in diesem Bereich ist schon sehr solide. Was denkst du selbst darüber?"
            ],
            'neutral': [
                f"Hier sehe ich sowohl Stärken als auch Potenzial für Verbesserungen. Die Grundlagen stimmen, aber wir können noch verfeinern.",
                f"Guter Ansatz! Einige Aspekte funktionieren schon gut, andere können wir gemeinsam optimieren. Was fällt dir selbst auf?",
                f"Solide Basis! Es gibt bereits positive Elemente, aber auch Bereiche wo wir noch arbeiten können."
            ],
            'critical': [
                f"Hier können wir gemeinsam viel erreichen! Es gibt einige Aspekte, die wir verbessern sollten, aber das ist völlig normal.",
                f"Das wird! Ich höre schon gute Ansätze, aber wir sollten an der Präzision arbeiten. Hast du Fragen zu diesem Abschnitt?",
                f"Kein Problem - solche Herausforderungen gehören zum Lernen dazu! Lass uns schauen, wie wir das angehen können."
            ]
        }
    
    import random
    return random.choice(responses.get(feedback_type, responses['neutral']))


# Test-Funktion
async def test_llm_integration():
    """Test der LLM Integration"""
    
    test_request = {
        'segment': {
            'id': 1,
            'startTime': 0.0,
            'endTime': 30.0,
            'feedback': 'good'
        },
        'musicContext': {
            'referenceInstrument': 'Klavier',
            'userInstrument': 'Klavier'
        },
        'userContext': {
            'language': 'Deutsch',
            'simpleLanguage': False,
            'personalMessage': 'Ich möchte mein Timing verbessern'
        },
        'type': 'initial'
    }
    
    result = await handle_llm_feedback_request(test_request)
    print("=== LLM TEST RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Test ausführen
    asyncio.run(test_llm_integration())
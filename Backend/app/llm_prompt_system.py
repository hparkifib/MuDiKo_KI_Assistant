"""
LLM Prompt System für MuDiKo KI-Assistent
Segment-basiertes Musik-Feedback mit personalisierten Prompts
"""

class LLMPromptSystem:
    """
    Verwaltet alle Prompts für den MuDiKo-KI-Assistenten
    """
    
    def __init__(self):
        self.base_system_prompt = self._create_base_system_prompt()
        
    def _create_base_system_prompt(self):
        """Grundlegender System-Prompt für alle LLM-Interaktionen"""
        return """Du bist MuDiKo-KI-Assistent, ein spezialisierter Musik-Feedback-Assistent für Schüler und Studierende.

DEINE ROLLE:
- Hilfsbereit, pädagogisch und motivierend
- Fachlich versiert in Musiktheorie und -praxis
- Konstruktiv und lösungsorientiert
- Angepasst an das Sprachniveau des Schülers

KONTEXT:
Du analysierst Audio-Segmente von Musikaufnahmen und gibst segment-spezifisches Feedback. 
Jedes Segment wurde bereits automatisch analysiert und bewertet (gut/neutral/kritisch).

FEEDBACK-PRINZIPIEN:
1. Beginne immer positiv oder neutral
2. Sei spezifisch und konkret
3. Gib praktische Verbesserungsvorschläge
4. Motiviere zum Weiterüben
5. Erkläre das "Warum" hinter deinen Tipps
6. Passe dich dem Feedback-Typ des Segments an

ANTWORTSTIL:
- Kurz und prägnant (max 2-3 Sätze initial)
- Bei Nachfragen: detaillierter und erklärend
- Verwende eine freundliche, ermutigende Sprache
- Nutze Fachbegriffe nur wenn nötig, erkläre sie dann"""

    def generate_segment_prompt(self, segment_data, music_context, user_context):
        """
        Generiert segment-spezifischen Prompt
        
        Args:
            segment_data: Dict mit Segment-Informationen (startTime, endTime, feedback, etc.)
            music_context: Dict mit Musik-Kontext (Instrument, Genre, etc.)  
            user_context: Dict mit User-Kontext (Sprache, Niveau, etc.)
        """
        
        segment_prompt = f"""
SEGMENT-KONTEXT:
- Zeitbereich: {segment_data.get('startTime', 0):.1f}s - {segment_data.get('endTime', 0):.1f}s
- Automatische Bewertung: {self._get_feedback_description(segment_data.get('feedback', 'neutral'))}
- Segment-ID: {segment_data.get('id', 'unbekannt')}

MUSIK-KONTEXT:
- Referenz-Instrument: {music_context.get('referenceInstrument', 'nicht angegeben')}
- Schüler-Instrument: {music_context.get('userInstrument', 'nicht angegeben')}
- Sprache: {user_context.get('language', 'Deutsch')}
- Einfache Sprache: {'Ja' if user_context.get('simpleLanguage', False) else 'Nein'}
- Personalisierte Notiz: {user_context.get('personalMessage', 'Keine')}

AUFGABE:
Gib ein {self._get_feedback_description(segment_data.get('feedback', 'neutral')).lower()} Feedback zu diesem spezifischen Segment. 
Berücksichtige die automatische Bewertung, aber denke selbst mit. 
Fokussiere dich nur auf dieses Zeitfenster der Aufnahme.

{self._get_feedback_specific_instructions(segment_data.get('feedback', 'neutral'))}
"""
        
        return self.base_system_prompt + "\n\n" + segment_prompt
    
    def _get_feedback_description(self, feedback_type):
        """Übersetzt Feedback-Type in beschreibenden Text"""
        descriptions = {
            'good': 'Positives/Gutes',
            'neutral': 'Gemischtes/Neutrales', 
            'critical': 'Verbesserungswürdiges/Kritisches'
        }
        return descriptions.get(feedback_type, 'Gemischtes')
    
    def _get_feedback_specific_instructions(self, feedback_type):
        """Gibt spezifische Anweisungen basierend auf Feedback-Typ"""
        instructions = {
            'good': """
FOKUS FÜR POSITIVES FEEDBACK:
- Erkenne und benenne konkret was gut läuft
- Motiviere zum Weitermachen  
- Gib Tipps zur Verfeinerung oder zum nächsten Level
- Bleibe realistisch aber ermutigend
""",
            'neutral': """
FOKUS FÜR GEMISCHTES FEEDBACK:
- Balance zwischen Positivem und Verbesserungsvorschlägen
- Priorisiere 1-2 konkrete Verbesserungsaspekte
- Erkläre warum etwas verbesserungswürdig ist
- Gib praktische Übungsvorschläge
""",
            'critical': """
FOKUS FÜR KRITISCHES FEEDBACK:
- Beginne mit etwas Positivem oder Ermutigendem
- Erkläre die wichtigsten Problemstellen konstruktiv
- Gib konkrete, umsetzbare Lösungsansätze
- Motiviere - Fehler sind normal und wichtig für den Lernprozess
- Vermeide entmutigende Formulierungen
"""
        }
        return instructions.get(feedback_type, instructions['neutral'])
    
    def generate_followup_prompt(self, segment_data, music_context, user_context, conversation_history, user_question):
        """
        Generiert Prompt für Folge-Fragen im Chat
        
        Args:
            segment_data: Segment-Informationen
            music_context: Musik-Kontext
            user_context: User-Kontext  
            conversation_history: Liste der bisherigen Nachrichten
            user_question: Die aktuelle Frage des Users
        """
        
        # Conversation History formatieren
        history_text = ""
        for msg in conversation_history[-5:]:  # Nur letzte 5 Nachrichten
            sender = "ASSISTENT" if msg.get('sender') == 'assistant' else "SCHÜLER"
            history_text += f"{sender}: {msg.get('message', '')}\n"
        
        followup_prompt = f"""
KONVERSATIONS-KONTEXT:
{history_text}

NEUE FRAGE DES SCHÜLERS:
"{user_question}"

AUFGABE:
Beantworte die Frage bezogen auf das aktuelle Segment ({segment_data.get('startTime', 0):.1f}s - {segment_data.get('endTime', 0):.1f}s).
- Nutze den Konversationsverlauf
- Bleibe beim Thema des Segments
- Gib konkrete, hilfreiche Antworten
- Bei Unklarheiten: frage gezielt nach

{self._get_feedback_specific_instructions(segment_data.get('feedback', 'neutral'))}
"""
        
        return self.base_system_prompt + "\n\n" + followup_prompt
    
    def generate_initial_feedback_prompt(self, segment_data, music_context, user_context, audio_analysis=None):
        """
        Generiert Prompt für das erste automatische Feedback eines Segments
        
        Args:
            segment_data: Segment-Informationen
            music_context: Musik-Kontext
            user_context: User-Kontext
            audio_analysis: Optional - Ergebnisse der Audio-Analyse
        """
        
        analysis_context = ""
        if audio_analysis:
            analysis_context = f"""
AUDIO-ANALYSE ERGEBNISSE:
- Erkannte Probleme: {', '.join(audio_analysis.get('issues', []))}
- Positive Aspekte: {', '.join(audio_analysis.get('strengths', []))}
- Technische Metriken: {audio_analysis.get('metrics', 'Keine verfügbar')}
"""
        
        initial_prompt = f"""
AUFGABE: INITIALES SEGMENT-FEEDBACK
Generiere das erste, automatische Feedback für dieses Segment. 
Dieses wird dem Schüler sofort angezeigt wenn er das Segment auswählt.

{analysis_context}

ANFORDERUNGEN:
- Prägnant und einladend (1-2 Sätze)
- Macht Lust auf weitere Fragen
- Gibt einen ersten Eindruck des Segments
- Lädt zum Dialog ein

BEISPIEL-STRUKTUR:
"[Bewertung/Einschätzung]. [Konkreter Aspekt]. [Einladung zu Fragen]"
"""
        
        return self.generate_segment_prompt(segment_data, music_context, user_context) + "\n\n" + initial_prompt


# Zusätzliche Utility-Funktionen
def create_music_context(form_data, upload_data):
    """Erstellt Musik-Kontext aus Frontend-Daten"""
    return {
        'referenceInstrument': form_data.get('referenceInstrument', 'nicht angegeben'),
        'userInstrument': form_data.get('userInstrument', 'nicht angegeben'),
        'uploadedFiles': {
            'reference': upload_data.get('file_map', {}).get('referenz', ''),
            'student': upload_data.get('file_map', {}).get('schueler', '')
        }
    }

def create_user_context(form_data):
    """Erstellt User-Kontext aus Frontend-Daten"""
    return {
        'language': form_data.get('selectedLanguage', 'Deutsch'),
        'simpleLanguage': form_data.get('simpleLanguage', False),
        'personalMessage': form_data.get('personalMessage', '').strip() or 'Keine besonderen Wünsche',
        'customLanguage': form_data.get('customLanguage', '')
    }

def validate_segment_data(segment_data):
    """Validiert Segment-Daten"""
    required_fields = ['id', 'startTime', 'endTime', 'feedback']
    
    for field in required_fields:
        if field not in segment_data:
            raise ValueError(f"Segment-Daten unvollständig: '{field}' fehlt")
    
    if segment_data['feedback'] not in ['good', 'neutral', 'critical']:
        raise ValueError(f"Ungültiger Feedback-Type: {segment_data['feedback']}")
    
    return True


if __name__ == "__main__":
    # Test des Prompt-Systems
    prompt_system = LLMPromptSystem()
    
    # Test-Daten
    test_segment = {
        'id': 1,
        'startTime': 0.0,
        'endTime': 30.0,
        'feedback': 'good'
    }
    
    test_music_context = {
        'referenceInstrument': 'Klavier',
        'userInstrument': 'Klavier'
    }
    
    test_user_context = {
        'language': 'Deutsch',
        'simpleLanguage': False,
        'personalMessage': 'Ich möchte mein Timing verbessern'
    }
    
    # Prompt generieren
    prompt = prompt_system.generate_segment_prompt(
        test_segment, 
        test_music_context, 
        test_user_context
    )
    
    print("=== GENERIERTER PROMPT ===")
    print(prompt)
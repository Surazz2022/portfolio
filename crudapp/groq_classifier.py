"""
Groq-based intent classifier for the portfolio chatbot.
Uses LLM understanding for accurate, context-aware intent detection.
Falls back to the local ML model if Groq is unavailable or the API key is not set.
"""
import os

VALID_INTENTS = {
    'greeting', 'about', 'skills', 'experience', 'contact',
    'availability', 'job_offer', 'research', 'projects', 'education', 'default'
}

SYSTEM_PROMPT = """You are an intent classifier for a portfolio chatbot representing Suraj Kharal, an AI/ML Engineer from Nepal.

Your job is to read the user's message — along with any conversation history — and return the single most appropriate intent.

Available intents:
- greeting       : casual greetings — hi, hello, hey, good morning, namaste, etc.
- about          : who Suraj is, his background, profile, summary, what he does professionally
- skills         : his technical skills, tools, frameworks, programming languages, tech stack
- experience     : his work history, current and past jobs, companies, roles, career journey
- contact        : how to reach him — email, phone, location, LinkedIn, GitHub, social links
- availability   : whether he is open to work, research positions, collaborations, new opportunities
- job_offer      : someone actively offering him a job, internship, PhD, fellowship, scholarship, or research role
- research       : his research interests, academic focus, what he is investigating, publications, academic goals
- projects       : projects he has built, his GitHub work, portfolio work, specific apps or pipelines
- education      : his degree, GPA, university, certifications, courses, academic background
- default        : off-topic questions, things not mentioned in the portfolio, or anything that doesn't fit above

Context rules (IMPORTANT):
- Use the conversation history to resolve follow-up messages.
- If the previous topic was research and the user says "tell me more" or "what about that?" → classify as research.
- If the previous topic was projects and the user asks "and the second one?" → classify as projects.
- Short, ambiguous messages like "elaborate", "continue", "what else?" should inherit the last discussed topic.
- Questions about salary, age, personal life, or anything clearly outside the portfolio → default.
- Questions about published papers, conferences, grants (not mentioned in portfolio) → research (the response generator will handle the honest denial).

Respond with ONLY the intent name in lowercase. One word. No punctuation. No explanation."""


class GroqIntentClassifier:
    """Context-aware intent classifier backed by Groq LLM."""

    def __init__(self):
        self._client = None
        self._available = None

    def _get_client(self):
        if self._available is False:
            return None
        if self._client is not None:
            return self._client

        api_key = os.environ.get('GROQ_API_KEY', '').strip()
        if not api_key:
            self._available = False
            print("Groq classifier: GROQ_API_KEY not set — using ML fallback.")
            return None

        try:
            from groq import Groq
            self._client = Groq(api_key=api_key)
            self._available = True
            print("Groq classifier: ready.")
            return self._client
        except ImportError:
            self._available = False
            print("Groq classifier: groq package not installed — using ML fallback.")
            return None

    def is_available(self):
        return self._get_client() is not None

    def classify(self, user_message, conversation_history=None):
        """
        Classify intent using Groq with full conversation context.
        Returns intent string, or None if Groq is unavailable (triggers ML fallback).
        """
        client = self._get_client()
        if not client:
            return None

        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Send last 8 messages as context so Groq understands follow-ups
            if conversation_history:
                for msg in conversation_history[-8:]:
                    role = "user" if msg.get('sender') == 'user' else "assistant"
                    content = msg.get('message', '').strip()
                    if content:
                        messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=10,
                temperature=0.0,
            )

            raw = response.choices[0].message.content.strip().lower()
            intent = raw.split()[0] if raw else 'default'
            return intent if intent in VALID_INTENTS else 'default'

        except Exception as e:
            print(f"Groq classification error: {e}")
            return None


_groq_classifier_instance = None


def get_groq_classifier():
    global _groq_classifier_instance
    if _groq_classifier_instance is None:
        _groq_classifier_instance = GroqIntentClassifier()
    return _groq_classifier_instance

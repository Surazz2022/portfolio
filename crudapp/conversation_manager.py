"""
Conversation State Manager
Handles conversation flow, state transitions, and context management
Works with both database (local) and in-memory (serverless) storage
"""
import os
import uuid
import time
from .models import ChatbotConversation, PersonalInfo

# In-memory session storage for serverless environments
_in_memory_sessions = {}

IS_SERVERLESS = os.environ.get('VERCEL', False) or os.environ.get('SERVERLESS', False)

SESSION_TTL_SECONDS = 3600  # 1 hour


class InMemoryConversation:
    """Lightweight conversation object for serverless environments"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.conversation_state = 'initial'
        self.conversation_history = []
        self.context = {}
        self.created_at = time.time()
        self.last_active = time.time()

    def is_expired(self):
        return (time.time() - self.last_active) > SESSION_TTL_SECONDS

    def touch(self):
        self.last_active = time.time()

    def save(self):
        """No-op for in-memory storage (already stored in dict)"""
        pass


class ConversationManager:
    """Manages conversation state and flow"""

    @staticmethod
    def get_or_create_session(session_id=None):
        """Get existing session or create a new one"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if IS_SERVERLESS:
            # Expire session if inactive for more than 1 hour
            if session_id in _in_memory_sessions:
                existing = _in_memory_sessions[session_id]
                if existing.is_expired():
                    del _in_memory_sessions[session_id]
                else:
                    existing.touch()
                    return existing, False

            conversation = InMemoryConversation(session_id)
            _in_memory_sessions[session_id] = conversation
            # Clean up expired sessions
            expired = [k for k, v in _in_memory_sessions.items() if v.is_expired()]
            for k in expired:
                del _in_memory_sessions[k]
            return conversation, True
        else:
            # Use database on local
            try:
                import datetime
                from django.utils import timezone
                expiry_threshold = timezone.now() - datetime.timedelta(hours=1)

                # Expire old sessions by deleting them so get_or_create treats them as new
                ChatbotConversation.objects.filter(
                    session_id=session_id,
                    updated_at__lt=expiry_threshold
                ).delete()

                conversation, created = ChatbotConversation.objects.get_or_create(
                    session_id=session_id,
                    defaults={
                        'conversation_state': 'initial',
                        'conversation_history': [],
                        'context': {}
                    }
                )
                return conversation, created
            except Exception:
                # Fallback to in-memory if DB fails
                if session_id in _in_memory_sessions:
                    existing = _in_memory_sessions[session_id]
                    if not existing.is_expired():
                        existing.touch()
                        return existing, False
                conversation = InMemoryConversation(session_id)
                _in_memory_sessions[session_id] = conversation
                return conversation, True
    
    @staticmethod
    def add_message_to_history(conversation, message, sender='user'):
        """Add a message to conversation history"""
        if not conversation.conversation_history:
            conversation.conversation_history = []
        
        conversation.conversation_history.append({
            'message': message,
            'sender': sender,
            'timestamp': time.time()
        })
        
        # Keep only last 20 messages to avoid bloating
        if len(conversation.conversation_history) > 20:
            conversation.conversation_history = conversation.conversation_history[-20:]
        
        conversation.save()
    
    @staticmethod
    def update_state(conversation, new_state, context_data=None):
        """Update conversation state"""
        conversation.conversation_state = new_state
        if context_data:
            conversation.context.update(context_data)
        conversation.save()
    
    @staticmethod
    def get_initial_greeting(personal_info):
        """Generate varied initial greeting with options"""
        if personal_info:
            name = personal_info.full_name
            linkedin = personal_info.linkedin_url
            github = personal_info.github_url
            email = personal_info.email
        else:
            name = 'Suraj Kharal'
            linkedin = 'https://www.linkedin.com/in/suraj-kharal-baa9271b1/'
            github = 'https://github.com/Surazz2022'
            email = 'surz.khl49@gmail.com'
        
        greeting = (
            f"Hello! 👋 I'm an AI assistant representing **{name}**.\n\n"
            f"Would you like to:\n\n"
            f"1️⃣ **View his LinkedIn profile** (say 'linkedin' or '1')\n"
            f"2️⃣ **View his GitHub repositories** (say 'github' or '2')\n"
            f"3️⃣ **Send him an email** (say 'email' or '3')\n\n"
            f"Or say **Skip** to start chatting directly."
        )
        
        return {
            'message': greeting,
            'options': {
                'linkedin_url': linkedin,
                'github_url': github,
                'email': email,
                'email_subject': 'Portfolio Inquiry — Suraj Kharal'
            }
        }
    
    @staticmethod
    def handle_initial_response(conversation, user_message, personal_info):
        """Handle user response during initial greeting flow"""
        message_lower = user_message.lower().strip()
        
        # Check if user wants to view LinkedIn
        if any(word in message_lower for word in ['linkedin', 'linked in', 'profile', '1', 'first', 'one']):
            ConversationManager.update_state(conversation, 'linkedin_question')
            return {
                'response': "Great! Would you like me to open {name}'s LinkedIn profile? (Yes/No/Skip)".format(
                    name=personal_info.full_name if personal_info else 'Suraj Kharal'
                ),
                'action': 'linkedin_question',
                'options': {
                    'linkedin_url': personal_info.linkedin_url if personal_info and personal_info.linkedin_url else 'https://www.linkedin.com/in/suraj-kharal-baa9271b1/'
                }
            }
        
        # Check if user wants to view GitHub
        elif any(word in message_lower for word in ['github', 'git hub', 'repositories', 'repos', 'code', '2', 'second', 'two']):
            ConversationManager.update_state(conversation, 'github_question')
            return {
                'response': "Great! Would you like me to open {name}'s GitHub profile? (Yes/No/Skip)".format(
                    name=personal_info.full_name if personal_info else 'Suraj Kharal'
                ),
                'action': 'github_question',
                'options': {
                    'github_url': personal_info.github_url if personal_info and personal_info.github_url else 'https://github.com/Surazz2022'
                }
            }
        
        # Check if user wants to send email
        elif any(word in message_lower for word in ['email', 'mail', 'send', 'contact', '3', 'third', 'three']):
            ConversationManager.update_state(conversation, 'email_question')
            return {
                'response': "Perfect! Would you like me to open your email client to send {name} an email with the subject 'Portfolio Inquiry — Suraj Kharal'? (Yes/No/Skip)".format(
                    name=personal_info.full_name if personal_info else 'Suraj Kharal'
                ),
                'action': 'email_question',
                'options': {
                    'email': personal_info.email if personal_info else 'surz.khl49@gmail.com',
                    'email_subject': 'Portfolio Inquiry — Suraj Kharal'
                }
            }
        
        # Skip all
        elif any(word in message_lower for word in ['skip', 'none', 'no thanks', 'not now', 'chat', 'start', 'begin']):
            ConversationManager.update_state(conversation, 'normal')
            return {
                'response': "No problem! Feel free to ask about research interests, skills, projects, experience, or contact details.",
                'action': 'normal',
                'options': {}
            }
        
        # Default - ask again
        else:
            return {
                'response': "I didn't quite understand. Please choose:\n• **LinkedIn** (say 'linkedin' or '1')\n• **GitHub** (say 'github' or '2')\n• **Email** (say 'email' or '3')\n• **Skip** (to start chatting)",
                'action': 'initial',
                'options': {}
            }
    
    @staticmethod
    def handle_state_response(conversation, user_message, personal_info):
        """Handle response based on current conversation state"""
        message_lower = user_message.lower().strip()
        state = conversation.conversation_state
        
        if state == 'linkedin_question':
            if any(word in message_lower for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                ConversationManager.update_state(conversation, 'github_question')
                linkedin_url = personal_info.linkedin_url if personal_info and personal_info.linkedin_url else 'https://www.linkedin.com/in/suraj-kharal-baa9271b1/'
                return {
                    'response': f"Opening LinkedIn profile! 🔗\n\nWould you like to view {personal_info.full_name if personal_info else 'Suraj'}'s GitHub profile next? (Yes/No/Skip)",
                    'action': 'open_linkedin',
                    'options': {
                        'linkedin_url': linkedin_url,
                        'next_state': 'github_question'
                    }
                }
            elif any(word in message_lower for word in ['no', 'n', 'skip']):
                ConversationManager.update_state(conversation, 'github_question')
                return {
                    'response': f"Okay, moving on! Would you like to view {personal_info.full_name if personal_info else 'Suraj'}'s GitHub profile? (Yes/No/Skip)",
                    'action': 'github_question',
                    'options': {
                        'github_url': personal_info.github_url if personal_info and personal_info.github_url else 'https://github.com/Surazz2022'
                    }
                }
            else:
                return {
                    'response': "Please respond with Yes, No, or Skip.",
                    'action': 'linkedin_question',
                    'options': {}
                }
        
        elif state == 'github_question':
            if any(word in message_lower for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                ConversationManager.update_state(conversation, 'email_question')
                github_url = personal_info.github_url if personal_info and personal_info.github_url else 'https://github.com/Surazz2022'
                name = personal_info.full_name if personal_info else 'Suraj'
                return {
                    'response': f"Opening GitHub profile! 💻\n\nWould you like to send {name} an email as well? (Yes/No/Skip)",
                    'action': 'open_github',
                    'options': {
                        'github_url': github_url,
                        'next_state': 'email_question'
                    }
                }
            elif any(word in message_lower for word in ['no', 'n', 'skip']):
                ConversationManager.update_state(conversation, 'email_question')
                name = personal_info.full_name if personal_info else 'Suraj'
                return {
                    'response': f"No problem! Would you like to send {name} an email? (Yes/No/Skip)",
                    'action': 'email_question',
                    'options': {
                        'email': personal_info.email if personal_info else 'surz.khl49@gmail.com',
                        'email_subject': 'Portfolio Inquiry — Suraj Kharal'
                    }
                }
            else:
                return {
                    'response': "Please respond with Yes, No, or Skip.",
                    'action': 'github_question',
                    'options': {}
                }
        
        elif state == 'email_question':
            if any(word in message_lower for word in ['yes', 'y', 'sure', 'ok', 'okay', 'send']):
                ConversationManager.update_state(conversation, 'normal')
                email = personal_info.email if personal_info else 'surz.khl49@gmail.com'
                name = personal_info.full_name if personal_info else 'Suraj'
                # Varied responses after email
                return {
                    'response': f"Opening email client! 📧\n\nFeel free to ask me anything else about {name}.",
                    'action': 'open_email',
                    'options': {
                        'email': email,
                        'email_subject': 'Portfolio Inquiry — Suraj Kharal'
                    }
                }
            elif any(word in message_lower for word in ['no', 'n', 'skip']):
                ConversationManager.update_state(conversation, 'normal')
                name = personal_info.full_name if personal_info else 'Suraj'
                # Varied responses
                return {
                    'response': f"No problem! You can ask me about {name}'s research interests, skills, projects, or experience.",
                    'action': 'normal',
                    'options': {}
                }
            else:
                return {
                    'response': "Please respond with Yes, No, or Skip.",
                    'action': 'email_question',
                    'options': {}
                }
        
        return None

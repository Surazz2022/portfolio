"""
Conversation State Manager
Handles conversation flow, state transitions, and context management
Works with both database (local) and in-memory (serverless) storage
"""
import os
import uuid
import random
from .models import ChatbotConversation, PersonalInfo

# In-memory session storage for serverless environments
_in_memory_sessions = {}

IS_SERVERLESS = os.environ.get('VERCEL', False) or os.environ.get('SERVERLESS', False)


class InMemoryConversation:
    """Lightweight conversation object for serverless environments"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.conversation_state = 'initial'
        self.conversation_history = []
        self.context = {}

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
            # Use in-memory storage on serverless
            if session_id in _in_memory_sessions:
                return _in_memory_sessions[session_id], False
            else:
                conversation = InMemoryConversation(session_id)
                _in_memory_sessions[session_id] = conversation
                # Clean up old sessions (keep max 1000)
                if len(_in_memory_sessions) > 1000:
                    oldest_keys = list(_in_memory_sessions.keys())[:500]
                    for key in oldest_keys:
                        del _in_memory_sessions[key]
                return conversation, True
        else:
            # Use database on local
            try:
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
                    return _in_memory_sessions[session_id], False
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
            'timestamp': str(uuid.uuid4())  # Simple timestamp alternative
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
        
        # Varied greeting messages
        greeting_templates = [
            f"Hello! 👋 I'm an AI assistant representing **{name}**.\n\nI'd like to help you get to know him better. Would you like to:\n\n1️⃣ **View his LinkedIn profile** (say 'linkedin' or '1')\n2️⃣ **View his GitHub repositories** (say 'github' or '2')\n3️⃣ **Send him an email** (say 'email' or '3') - with pre-filled subject: 'Offer letter for Senior AI Engineer'\n\nOr say **Skip** to start chatting directly.\n\nWhat would you like to do first?",
            
            f"Hi there! 👋 Welcome! I'm here to help you learn about **{name}**.\n\nQuick options:\n\n1️⃣ **LinkedIn profile** (say 'linkedin')\n2️⃣ **GitHub repositories** (say 'github')\n3️⃣ **Send email** (say 'email') - Subject: 'Offer letter for Senior AI Engineer'\n\nOr just **Skip** to start asking questions!\n\nWhat interests you?",
            
            f"Welcome! 👋 I'm an AI assistant for **{name}**.\n\nWould you like to:\n\n1️⃣ Check out his **LinkedIn** (say 'linkedin')\n2️⃣ Browse his **GitHub** (say 'github')\n3️⃣ **Email him** (say 'email') - Pre-filled: 'Offer letter for Senior AI Engineer'\n\nOr say **Skip** to chat directly!\n\nHow can I help?",
        ]
        
        greeting = random.choice(greeting_templates)
        
        return {
            'message': greeting,
            'options': {
                'linkedin_url': linkedin,
                'github_url': github,
                'email': email,
                'email_subject': 'Offer letter for Senior AI Engineer'
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
                'response': "Perfect! Would you like me to open your email client to send {name} an email with the subject 'Offer letter for Senior AI Engineer'? (Yes/No/Skip)".format(
                    name=personal_info.full_name if personal_info else 'Suraj Kharal'
                ),
                'action': 'email_question',
                'options': {
                    'email': personal_info.email if personal_info else 'surz.khl49@gmail.com',
                    'email_subject': 'Offer letter for Senior AI Engineer'
                }
            }
        
        # Skip all
        elif any(word in message_lower for word in ['skip', 'none', 'no thanks', 'not now', 'chat', 'start', 'begin']):
            ConversationManager.update_state(conversation, 'normal')
            skip_responses = [
                "No problem! How can I help you today? You can ask about skills, experience, or submit a job offer.",
                "Sure! Let's chat. Feel free to ask about skills, experience, contact info, or job offers.",
                "Great! What would you like to know? I can tell you about skills, experience, availability, or help with job offers.",
            ]
            return {
                'response': random.choice(skip_responses),
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
                github_responses = [
                    f"Opening GitHub profile! 💻\n\nWould you like to send {name} an email with the subject 'Offer letter for Senior AI Engineer'? (Yes/No/Skip)",
                    f"GitHub opening! 💻\n\nNext, want to email {name}? Subject will be 'Offer letter for Senior AI Engineer'. (Yes/No/Skip)",
                    f"Here's the GitHub! 💻\n\nReady to send {name} an email? (Yes/No/Skip)",
                ]
                return {
                    'response': random.choice(github_responses),
                    'action': 'open_github',
                    'options': {
                        'github_url': github_url,
                        'next_state': 'email_question'
                    }
                }
            elif any(word in message_lower for word in ['no', 'n', 'skip']):
                ConversationManager.update_state(conversation, 'email_question')
                name = personal_info.full_name if personal_info else 'Suraj'
                skip_responses = [
                    f"Okay! Would you like to send {name} an email with the subject 'Offer letter for Senior AI Engineer'? (Yes/No/Skip)",
                    f"Sure! Next - email {name}? Subject: 'Offer letter for Senior AI Engineer'. (Yes/No/Skip)",
                    f"No problem! Want to email {name}? (Yes/No/Skip)",
                ]
                return {
                    'response': random.choice(skip_responses),
                    'action': 'email_question',
                    'options': {
                        'email': personal_info.email if personal_info else 'surz.khl49@gmail.com',
                        'email_subject': 'Offer letter for Senior AI Engineer'
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
                email_responses = [
                    f"Opening email client! 📧\n\nGreat! I've opened your email client. Feel free to ask me anything else about {name} or submit a job offer!",
                    f"Email client opening! 📧\n\nPerfect! You can now send the email. Is there anything else you'd like to know about {name}?",
                    f"Email ready! 📧\n\nYour email client should be open now. Need any other information about {name}?",
                ]
                return {
                    'response': random.choice(email_responses),
                    'action': 'open_email',
                    'options': {
                        'email': email,
                        'email_subject': 'Offer letter for Senior AI Engineer'
                    }
                }
            elif any(word in message_lower for word in ['no', 'n', 'skip']):
                ConversationManager.update_state(conversation, 'normal')
                name = personal_info.full_name if personal_info else 'Suraj'
                # Varied responses
                skip_responses = [
                    f"No problem! How can I help you today? You can ask about {name}'s skills, experience, or submit a job offer.",
                    f"Sure! What would you like to know? Feel free to ask about {name}'s background, skills, or availability.",
                    f"Okay! I'm here to help. Ask me about {name}'s experience, skills, contact info, or job opportunities.",
                ]
                return {
                    'response': random.choice(skip_responses),
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

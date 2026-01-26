# Context-Aware ML Chatbot - Enhanced Features

## Overview
The chatbot has been enhanced with:
- **Context-aware conversations** - Remembers previous messages
- **Initial greeting flow** - Guides users through LinkedIn, GitHub, and Email options
- **Session management** - Tracks conversations across interactions
- **Improved ML understanding** - Better intent prediction with context

## New Features

### 1. Initial Greeting Flow
When a user first opens the chatbot, they are greeted with options to:
- **View LinkedIn profile** - Opens LinkedIn in a new tab
- **View GitHub repositories** - Opens GitHub in a new tab  
- **Send Email** - Opens email client with pre-filled subject: "Offer letter for Senior AI Engineer"

Users can respond with:
- **Yes** - Proceed with the option
- **No** - Skip to next option
- **Skip** - Skip all and start chatting

### 2. Context-Aware Conversations
- **Conversation History**: Tracks last 20 messages for context
- **State Management**: Remembers where you are in the conversation flow
- **Session Persistence**: Uses localStorage to maintain session across page refreshes

### 3. Enhanced ML Model
- **Context Integration**: Uses conversation history to better understand intent
- **State-Aware Predictions**: Considers current conversation state
- **Improved Accuracy**: Better predictions with more training data

## Technical Implementation

### New Models

#### ChatbotConversation
Stores conversation state and history:
- `session_id` - Unique identifier for each conversation
- `conversation_state` - Current state (initial, linkedin_question, github_question, email_question, normal, job_offer_flow)
- `conversation_history` - JSON array of messages
- `context` - Additional context data

### New Files

1. **`conversation_manager.py`** - Handles conversation flow and state transitions
2. **Enhanced `ml_chatbot.py`** - Added context-aware prediction methods
3. **Updated `views.py`** - Integrated conversation management
4. **Updated `Suraj.html`** - Frontend with session management and quick action buttons

### Conversation States

- `initial` - First greeting, asking about LinkedIn/GitHub/Email
- `linkedin_question` - Asking if user wants to view LinkedIn
- `github_question` - Asking if user wants to view GitHub
- `email_question` - Asking if user wants to send email
- `normal` - Regular conversation
- `job_offer_flow` - Job offer submission process

## Usage Flow

### First Time User
1. User opens chatbot
2. Bot greets with LinkedIn/GitHub/Email options
3. User chooses an option (e.g., "linkedin" or "1")
4. Bot asks for confirmation (Yes/No/Skip)
5. If Yes: Opens link and moves to next option
6. If No/Skip: Moves to next option
7. After all options: Enters normal conversation mode

### Returning User
- Session is maintained via localStorage
- Conversation continues from where it left off
- Context is preserved for better understanding

## Frontend Features

### Quick Action Buttons
When the bot mentions LinkedIn, GitHub, or Email, quick action buttons appear:
- 🔗 **Open LinkedIn** - Opens LinkedIn profile
- 💻 **Open GitHub** - Opens GitHub profile  
- 📧 **Send Email** - Opens email client with pre-filled subject

### Session Management
- Session ID stored in localStorage
- Persists across page refreshes
- Each browser tab gets its own session

## API Changes

### Updated Endpoint: `/api/chatbot/`

**Request:**
```json
{
    "message": "hello",
    "session_id": "session_123...",
    "is_first_message": true
}
```

**Response:**
```json
{
    "response": "Hello! 👋 I'm an AI assistant...",
    "action": "initial_greeting",
    "session_id": "session_123...",
    "options": {
        "linkedin_url": "https://...",
        "github_url": "https://...",
        "email": "email@example.com",
        "email_subject": "Offer letter for Senior AI Engineer"
    },
    "intent": "greeting"
}
```

## Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Test the Chatbot
1. Start server: `python manage.py runserver`
2. Open portfolio page
3. Click chatbot icon
4. Experience the new greeting flow!

## Admin Interface

### View Conversations
- Go to `/admin/`
- Click "Chatbot Conversations"
- View all active sessions and their states
- See conversation history and context

### Manage Training Data
- Add more training examples for better understanding
- Model automatically retrains when data changes

## Benefits

✅ **Better User Experience** - Guided flow for common actions  
✅ **Context Awareness** - Understands conversation flow  
✅ **Session Persistence** - Remembers across interactions  
✅ **Quick Actions** - One-click access to LinkedIn/GitHub/Email  
✅ **Improved Accuracy** - Better intent prediction with context  

## Future Enhancements

- Add more conversation states for complex flows
- Implement conversation analytics
- Add support for multiple languages
- Integrate with external APIs for richer responses
- Add conversation export functionality

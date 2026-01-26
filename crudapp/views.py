# crudapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Item, PersonalInfo, JobOffer, ChatbotTrainingData
from .forms import ItemForm, JobOfferForm
from .ml_chatbot import MLChatbotService
from .conversation_manager import ConversationManager
from .response_generator import ResponseGenerator

def item_list(request):
    items = Item.objects.all()
    return render(request, 'crudapp/item_list.html', {'items': items})

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'crudapp/item_form.html', {'form': form})

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'crudapp/item_form.html', {'form': form})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'crudapp/item_confirm_delete.html', {'item': item})

def Suraj(request):
    # Get personal info if exists, otherwise use defaults
    personal_info = PersonalInfo.objects.first()
    return render(request, 'crudapp/Suraj.html', {'personal_info': personal_info})


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_interact(request):
    """Handle chatbot interactions using ML model with context awareness"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', None)
        is_first_message = data.get('is_first_message', False)
        
        if not user_message:
            return JsonResponse({
                'response': 'Please enter a message.',
                'action': None
            })
        
        # Get or create conversation session
        conversation, is_new_session = ConversationManager.get_or_create_session(session_id)
        
        # Get personal info
        personal_info = PersonalInfo.objects.first()
        
        # Default responses if no personal info exists
        default_responses = {
            'name': 'Suraj Kharal',
            'title': 'Junior Machine Learning Engineer & Data Analyst',
            'email': 'surz.khl49@gmail.com',
            'phone': '+977-9869407702',
            'location': 'Devdaha 07, Rupandehi, Nepal',
            'bio': 'I am a motivated data professional with a good foundation in machine learning, statistics, and python programming.',
            'skills': 'Python, Machine Learning, Data Analysis, LSTM, ARIMA, Time Series Analysis, Data Pipelines',
            'experience': 'Junior ML Engineer at CognifyNow, Junior Data Analyst at NepseTrading',
            'availability': 'Available for opportunities',
            'preferred_roles': 'Machine Learning Engineer, Data Scientist, Data Analyst',
        }
        
        if personal_info:
            info = {
                'name': personal_info.full_name,
                'title': personal_info.title,
                'email': personal_info.email,
                'phone': personal_info.phone,
                'location': personal_info.location,
                'bio': personal_info.bio,
                'skills': personal_info.skills_summary,
                'experience': personal_info.experience_summary,
                'availability': personal_info.availability,
                'preferred_roles': personal_info.preferred_roles,
            }
        else:
            info = default_responses
        
        # Handle initial greeting flow - ONLY for first message or new session
        if is_new_session or (is_first_message and conversation.conversation_state == 'initial'):
            # Add user message to history
            ConversationManager.add_message_to_history(conversation, user_message, 'user')
            
            # Get initial greeting
            greeting_data = ConversationManager.get_initial_greeting(personal_info)
            
            # Add bot response to history
            ConversationManager.add_message_to_history(conversation, greeting_data['message'], 'bot')
            
            return JsonResponse({
                'response': greeting_data['message'],
                'action': 'initial_greeting',
                'session_id': conversation.session_id,
                'options': greeting_data['options'],
                'intent': 'greeting'
            })
        
        # Handle state-specific responses (LinkedIn, GitHub, Email questions)
        if conversation.conversation_state in ['linkedin_question', 'github_question', 'email_question']:
            ConversationManager.add_message_to_history(conversation, user_message, 'user')
            state_response = ConversationManager.handle_state_response(conversation, user_message, personal_info)
            
            if state_response:
                ConversationManager.add_message_to_history(conversation, state_response['response'], 'bot')
                return JsonResponse({
                    'response': state_response['response'],
                    'action': state_response['action'],
                    'session_id': conversation.session_id,
                    'options': state_response.get('options', {}),
                    'intent': state_response['action']
                })
        
        # Handle initial greeting response (when user chooses an option or skips)
        # Only handle if still in initial state AND message is about linkedin/github/email/skip
        if conversation.conversation_state == 'initial' and not is_new_session:
            message_lower = user_message.lower().strip()
            # Check if user is responding to initial greeting options
            is_greeting_response = any(word in message_lower for word in [
                'linkedin', 'linked in', 'github', 'git hub', 'email', 'mail', 
                'skip', 'none', '1', '2', '3', 'first', 'second', 'third'
            ])
            
            if is_greeting_response:
                ConversationManager.add_message_to_history(conversation, user_message, 'user')
                initial_response = ConversationManager.handle_initial_response(conversation, user_message, personal_info)
                
                if initial_response:
                    ConversationManager.add_message_to_history(conversation, initial_response['response'], 'bot')
                    
                    # If user skipped, move to normal conversation
                    if initial_response['action'] == 'normal':
                        ConversationManager.update_state(conversation, 'normal')
                    
                    return JsonResponse({
                        'response': initial_response['response'],
                        'action': initial_response['action'],
                        'session_id': conversation.session_id,
                        'options': initial_response.get('options', {}),
                        'intent': initial_response['action']
                    })
            else:
                # User asked a normal question, skip greeting flow
                ConversationManager.update_state(conversation, 'normal')
        
        # Normal conversation flow with ML model
        ConversationManager.add_message_to_history(conversation, user_message, 'user')
        
        # Initialize ML chatbot service
        ml_chatbot = MLChatbotService()
        
        # Get conversation history for context
        history = conversation.conversation_history[:-1] if len(conversation.conversation_history) > 1 else []
        
        # Predict intent with context
        prediction = ml_chatbot.predict_with_context(
            user_message,
            conversation_state=conversation.conversation_state,
            conversation_history=history
        )
        
        predicted_intent = prediction['intent']
        
        # Get training data for similar message matching
        training_data = ChatbotTrainingData.objects.all()
        training_tuples = [(item.user_message, item.intent, item.response) for item in training_data]
        
        # Try to find a matching response from training data
        response = None
        action = None
        
        # First, try to find exact or similar matches in training data
        if training_tuples:
            similar_messages = ml_chatbot.get_similar_messages(user_message, training_tuples, top_n=1)
            if similar_messages and similar_messages[0]['similarity'] > 0.5:
                # Use the response from similar training data
                response = similar_messages[0]['response']
                predicted_intent = similar_messages[0]['intent']
        
        # If no good match found, use enhanced response generator
        if not response:
            # Use enhanced response generator for varied, context-aware responses
            response = ResponseGenerator.generate_response(
                predicted_intent, 
                personal_info, 
                user_message,
                context={'conversation_history': history}
            )
        
        # Handle job offer flow
        if predicted_intent == 'job_offer' or any(word in user_message.lower() for word in ['job offer', 'offer', 'position', 'role', 'opportunity', 'hire', 'recruit']):
            action = "offer_flow"
            ConversationManager.update_state(conversation, 'job_offer_flow')
        
        # Add bot response to history
        ConversationManager.add_message_to_history(conversation, response, 'bot')
        
        return JsonResponse({
            'response': response,
            'action': action,
            'session_id': conversation.session_id,
            'intent': predicted_intent,
            'confidence': prediction.get('confidence', 0.0)
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'response': 'Sorry, I encountered an error. Please try again.',
            'error': str(e)
        }, status=500)


def _generate_response_from_intent(intent, info, user_message):
    """Generate response based on predicted intent (fallback method)"""
    # This is now a fallback - main responses use ResponseGenerator
    personal_info = PersonalInfo.objects.first()
    return ResponseGenerator.generate_response(intent, personal_info, user_message)


@csrf_exempt
@require_http_methods(["POST"])
def submit_job_offer(request):
    """Handle job offer submission"""
    try:
        data = json.loads(request.body)
        form = JobOfferForm(data)
        
        if form.is_valid():
            job_offer = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Thank you! Your job offer for "{job_offer.job_title}" at {job_offer.company_name} has been submitted successfully. {job_offer.recruiter_name} will review it and get back to you soon!',
                'offer_id': job_offer.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.',
                'errors': form.errors
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting the job offer.',
            'error': str(e)
        }, status=500)


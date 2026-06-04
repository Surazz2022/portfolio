# crudapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Item, PersonalInfo, JobOffer, ChatbotTrainingData
from .forms import ItemForm, JobOfferForm
from .ml_chatbot import get_chatbot_service
from .groq_classifier import get_groq_classifier
from .conversation_manager import ConversationManager
from .response_generator import ResponseGenerator


class DefaultPersonalInfo:
    """Fallback personal info when database is empty (e.g., on Vercel)"""
    full_name = 'Suraj Kharal'
    title = 'Artificial Intelligence Engineer'
    email = 'surz.khl49@gmail.com'
    phone = '+977-9869407702'
    location = 'Devdaha 07, Rupandehi, Nepal'
    linkedin_url = 'https://www.linkedin.com/in/suraj-kharal-baa9271b1/'
    github_url = 'https://github.com/Surazz2022'
    bio = 'I am an AI/ML engineer with hands-on experience building autonomous agentic systems, RAG pipelines, and end-to-end data solutions across finance, healthcare, and e-commerce domains. My work spans LLM-powered tools, document intelligence, and multimodal AI — grounded in real production environments. I am actively seeking research opportunities at the intersection of agentic AI, natural language processing, and AI robustness in domain-specific applications.'
    skills_summary = 'Python, LangChain, LangGraph, RAG, FAISS, Sentence Transformers, Groq, Llama, Ollama, FastAPI, Django, Docker, PostgreSQL, Qdrant, OCR, Machine Learning, Data Analysis'
    experience_summary = 'Artificial Intelligence Engineer at NepaWorks, Junior Machine Learning Engineer at CognifyNow, Junior Data Analyst at NepseTrading'
    availability = 'Available for opportunities'
    preferred_roles = 'AI Engineer, ML Engineer, Data Scientist, Backend Developer'
    salary_expectation = None
    work_preference = 'any'

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
    try:
        personal_info = PersonalInfo.objects.first()
    except Exception:
        personal_info = None
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

        # Get personal info (gracefully handle missing DB, use defaults on Vercel)
        try:
            personal_info = PersonalInfo.objects.first()
        except Exception:
            personal_info = None

        if not personal_info:
            personal_info = DefaultPersonalInfo()
        
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
        
        # Normal conversation flow
        ConversationManager.add_message_to_history(conversation, user_message, 'user')

        # History for context (exclude the message just added)
        history = conversation.conversation_history[:-1] if len(conversation.conversation_history) > 1 else []

        predicted_intent = None
        confidence = 1.0

        # ── Step 1: Try Groq (LLM-based, context-aware) ──────────────────────
        groq = get_groq_classifier()
        predicted_intent = groq.classify(user_message, conversation_history=history)

        # ── Step 2: ML fallback if Groq unavailable or errored ───────────────
        if predicted_intent is None:
            ml_chatbot = get_chatbot_service()
            prediction = ml_chatbot.predict_with_context(
                user_message,
                conversation_state=conversation.conversation_state,
                conversation_history=history
            )
            predicted_intent = prediction['intent']
            confidence = prediction.get('confidence', 0.0)

            # Follow-up resolution for ML fallback (Groq handles this natively)
            if predicted_intent == 'default':
                last_intent = conversation.context.get('last_intent')
                if last_intent:
                    msg_lower = user_message.lower().strip()
                    follow_up_signals = [
                        'more', 'tell me more', 'elaborate', 'expand', 'continue',
                        'what about', 'that', 'it', 'first', 'second', 'third',
                        'explain', 'detail', 'further', 'again'
                    ]
                    if len(user_message.split()) <= 5 or any(s in msg_lower for s in follow_up_signals):
                        predicted_intent = last_intent

        # Store last intent for ML fallback follow-up resolution
        known_intents = {'about', 'skills', 'experience', 'contact', 'availability',
                         'research', 'projects', 'education'}
        if predicted_intent in known_intents:
            conversation.context['last_intent'] = predicted_intent
            conversation.save()

        response = None
        action = None

        # Use response generator — strictly portfolio-grounded
        response = ResponseGenerator.generate_response(
            predicted_intent,
            personal_info,
            user_message,
            context={'conversation_history': history}
        )

        # Handle job offer flow
        if predicted_intent == 'job_offer':
            action = "offer_flow"
            ConversationManager.update_state(conversation, 'job_offer_flow')

        ConversationManager.add_message_to_history(conversation, response, 'bot')

        return JsonResponse({
            'response': response,
            'action': action,
            'session_id': conversation.session_id,
            'intent': predicted_intent,
            'confidence': confidence
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
    try:
        personal_info = PersonalInfo.objects.first()
    except Exception:
        personal_info = None
    if not personal_info:
        personal_info = DefaultPersonalInfo()
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


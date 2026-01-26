"""
ML-based Chatbot Service
Uses scikit-learn for intent classification and response generation
"""
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from django.conf import settings
import joblib

class MLChatbotService:
    """Machine Learning Chatbot Service"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        # Convert Path object to string for os.path operations
        base_dir = str(settings.BASE_DIR)
        self.model_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'chatbot_model.pkl')
        self.vectorizer_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'vectorizer.pkl')
        self._ensure_model_directory()
        self._load_or_initialize_model()
    
    def _ensure_model_directory(self):
        """Ensure the model directory exists"""
        model_dir = os.path.dirname(self.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    def _load_or_initialize_model(self):
        """Load existing model or initialize a new one"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
            except Exception as e:
                print(f"Error loading model: {e}. Initializing new model.")
                self._initialize_model()
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new ML model"""
        # Create a pipeline with TF-IDF vectorizer and Naive Bayes classifier
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True,
                min_df=1,
                max_df=0.95
            )),
            ('classifier', MultinomialNB(alpha=1.0))
        ])
        self.vectorizer = None  # Will be part of the pipeline
    
    def train(self, training_data):
        """
        Train the model on provided training data
        
        Args:
            training_data: List of tuples (user_message, intent)
        """
        if not training_data or len(training_data) == 0:
            return False
        
        # Extract messages and intents
        messages = [item[0].lower().strip() for item in training_data]
        intents = [item[1] for item in training_data]
        
        # Train the model
        try:
            self.model.fit(messages, intents)
            
            # Save the trained model
            self._save_model()
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict_intent(self, user_message, conversation_history=None):
        """
        Predict the intent of a user message with context awareness
        
        Args:
            user_message: The user's message
            conversation_history: List of previous messages for context
            
        Returns:
            Predicted intent string
        """
        if not self.model:
            return 'default'
        
        try:
            # Clean and preprocess the message
            cleaned_message = user_message.lower().strip()
            
            # Check for questions about Suraj Kharal specifically
            suraj_keywords = ['suraj', 'kharal', 'suraj kharal', 'him', 'his', 'he']
            is_about_suraj = any(keyword in cleaned_message for keyword in suraj_keywords)
            
            # If conversation history is provided, add context
            if conversation_history and len(conversation_history) > 0:
                # Get last few messages for context
                recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
                context_text = " ".join([msg.get('message', '') for msg in recent_messages if isinstance(msg, dict)])
                # Combine context with current message for better understanding
                enhanced_message = f"{context_text} {cleaned_message}".strip()
            else:
                enhanced_message = cleaned_message
            
            # If asking about Suraj and no clear intent, default to 'about'
            if is_about_suraj and any(word in cleaned_message for word in ['who', 'what', 'tell', 'about', 'know']):
                # Check if it's really about the person
                if not any(word in cleaned_message for word in ['skill', 'experience', 'contact', 'email', 'phone']):
                    return 'about'
            
            # Predict intent
            intent = self.model.predict([enhanced_message])[0]
            
            # Get prediction probability
            probabilities = self.model.predict_proba([enhanced_message])[0]
            max_probability = max(probabilities)
            
            # If confidence is too low, return default
            if max_probability < 0.3:
                return 'default'
            
            return intent
        except Exception as e:
            print(f"Error predicting intent: {e}")
            return 'default'
    
    def predict_with_context(self, user_message, conversation_state=None, conversation_history=None):
        """
        Enhanced prediction that considers conversation state and history
        
        Args:
            user_message: The user's message
            conversation_state: Current state of the conversation
            conversation_history: Previous messages
            
        Returns:
            Dict with intent, confidence, and suggested actions
        """
        if not self.model:
            return {
                'intent': 'default',
                'confidence': 0.0,
                'actions': []
            }
        
        try:
            cleaned_message = user_message.lower().strip()
            
            # Handle state-specific responses
            if conversation_state == 'linkedin_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {
                        'intent': 'linkedin_yes',
                        'confidence': 1.0,
                        'actions': ['open_linkedin']
                    }
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {
                        'intent': 'linkedin_no',
                        'confidence': 1.0,
                        'actions': ['next_question']
                    }
            
            elif conversation_state == 'github_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {
                        'intent': 'github_yes',
                        'confidence': 1.0,
                        'actions': ['open_github']
                    }
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {
                        'intent': 'github_no',
                        'confidence': 1.0,
                        'actions': ['next_question']
                    }
            
            elif conversation_state == 'email_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'send']):
                    return {
                        'intent': 'email_yes',
                        'confidence': 1.0,
                        'actions': ['open_email']
                    }
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {
                        'intent': 'email_no',
                        'confidence': 1.0,
                        'actions': ['end_greeting']
                    }
            
            # Use ML model for normal conversation
            intent = self.predict_intent(user_message, conversation_history)
            probabilities = self.model.predict_proba([cleaned_message])[0]
            max_probability = max(probabilities)
            
            return {
                'intent': intent,
                'confidence': float(max_probability),
                'actions': []
            }
        except Exception as e:
            print(f"Error in predict_with_context: {e}")
            return {
                'intent': 'default',
                'confidence': 0.0,
                'actions': []
            }
    
    def get_similar_messages(self, user_message, training_data, top_n=3):
        """
        Find similar messages from training data using TF-IDF similarity
        
        Args:
            user_message: The user's message
            training_data: List of tuples (user_message, intent, response)
            top_n: Number of similar messages to return
            
        Returns:
            List of similar (message, intent, response) tuples
        """
        if not training_data or len(training_data) == 0:
            return []
        
        try:
            # Extract messages
            messages = [item[0].lower().strip() for item in training_data]
            messages.append(user_message.lower().strip())
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(messages)
            
            # Get similarity between user message and training messages
            user_vector = tfidf_matrix[-1]
            training_vectors = tfidf_matrix[:-1]
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(user_vector, training_vectors)[0]
            
            # Get top N similar messages
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            similar_messages = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    similar_messages.append({
                        'message': training_data[idx][0],
                        'intent': training_data[idx][1],
                        'response': training_data[idx][2],
                        'similarity': float(similarities[idx])
                    })
            
            return similar_messages
        except Exception as e:
            print(f"Error finding similar messages: {e}")
            return []
    
    def _save_model(self):
        """Save the trained model to disk"""
        try:
            joblib.dump(self.model, self.model_path)
            # Extract vectorizer from pipeline if needed
            if hasattr(self.model, 'named_steps'):
                vectorizer = self.model.named_steps.get('tfidf')
                if vectorizer:
                    joblib.dump(vectorizer, self.vectorizer_path)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def retrain_from_database(self):
        """Retrain the model using all data from ChatbotTrainingData"""
        from .models import ChatbotTrainingData
        
        training_data = ChatbotTrainingData.objects.all()
        
        if training_data.count() == 0:
            return False
        
        # Prepare data: (message, intent)
        data = [(item.user_message, item.intent) for item in training_data]
        
        return self.train(data)

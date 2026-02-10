"""
ML-based Chatbot Service
Uses scikit-learn for intent classification and response generation
Works in both local (with file persistence) and serverless (in-memory) environments
"""
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from django.conf import settings

# Default training data - used when database is unavailable (e.g., Vercel serverless)
DEFAULT_TRAINING_DATA = [
    # Greetings
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("hey", "greeting"),
    ("good morning", "greeting"),
    ("good afternoon", "greeting"),
    ("good evening", "greeting"),
    ("hi there", "greeting"),
    ("hey there", "greeting"),
    ("whats up", "greeting"),
    ("howdy", "greeting"),

    # About
    ("who is suraj", "about"),
    ("who is suraj kharal", "about"),
    ("tell me about suraj", "about"),
    ("tell me about him", "about"),
    ("who are you representing", "about"),
    ("what does suraj do", "about"),
    ("introduce suraj", "about"),
    ("who is this person", "about"),
    ("tell me about yourself", "about"),
    ("what is suraj background", "about"),
    ("describe suraj", "about"),
    ("who is he", "about"),
    ("about suraj", "about"),
    ("what do you know about suraj", "about"),

    # Skills
    ("what are his skills", "skills"),
    ("what skills does suraj have", "skills"),
    ("what technologies does he know", "skills"),
    ("what can suraj do", "skills"),
    ("technical skills", "skills"),
    ("programming languages", "skills"),
    ("what is he good at", "skills"),
    ("skills", "skills"),
    ("expertise", "skills"),
    ("what tools does he use", "skills"),
    ("does he know python", "skills"),
    ("does he know machine learning", "skills"),
    ("what frameworks does he use", "skills"),
    ("his tech stack", "skills"),

    # Experience
    ("what is his experience", "experience"),
    ("work experience", "experience"),
    ("where has he worked", "experience"),
    ("previous jobs", "experience"),
    ("career history", "experience"),
    ("professional background", "experience"),
    ("what companies has he worked for", "experience"),
    ("experience", "experience"),
    ("his work history", "experience"),
    ("where does he work", "experience"),
    ("current job", "experience"),
    ("past experience", "experience"),

    # Contact
    ("how can i contact him", "contact"),
    ("contact information", "contact"),
    ("email address", "contact"),
    ("phone number", "contact"),
    ("how to reach suraj", "contact"),
    ("contact details", "contact"),
    ("how do i get in touch", "contact"),
    ("contact", "contact"),
    ("email", "contact"),
    ("phone", "contact"),
    ("reach out", "contact"),
    ("his email", "contact"),
    ("his phone", "contact"),

    # Availability
    ("is he available", "availability"),
    ("is suraj looking for work", "availability"),
    ("availability", "availability"),
    ("is he open to opportunities", "availability"),
    ("what roles is he looking for", "availability"),
    ("is he hiring", "availability"),
    ("job status", "availability"),
    ("is he employed", "availability"),
    ("open to work", "availability"),
    ("looking for job", "availability"),

    # Job offer
    ("i have a job offer", "job_offer"),
    ("job opportunity", "job_offer"),
    ("we want to hire suraj", "job_offer"),
    ("i want to offer a position", "job_offer"),
    ("job offer", "job_offer"),
    ("hire him", "job_offer"),
    ("recruit suraj", "job_offer"),
    ("we have an opening", "job_offer"),
    ("position available", "job_offer"),
    ("offer letter", "job_offer"),
    ("submit job offer", "job_offer"),
    ("employment opportunity", "job_offer"),
]

# Singleton instance to avoid re-training on every request
_chatbot_instance = None


def get_chatbot_service():
    """Get or create the singleton MLChatbotService instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MLChatbotService()
    return _chatbot_instance


class MLChatbotService:
    """Machine Learning Chatbot Service"""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_serverless = os.environ.get('VERCEL', False) or os.environ.get('SERVERLESS', False)

        if not self.is_serverless:
            base_dir = str(settings.BASE_DIR)
            self.model_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'chatbot_model.pkl')
            self.vectorizer_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'vectorizer.pkl')
            self._ensure_model_directory()

        self._load_or_initialize_model()

    def _ensure_model_directory(self):
        """Ensure the model directory exists (local only)"""
        if self.is_serverless:
            return
        model_dir = os.path.dirname(self.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

    def _load_or_initialize_model(self):
        """Load existing model or initialize and train with default data"""
        loaded = False

        # Try loading from disk (local environment only)
        if not self.is_serverless:
            try:
                import joblib
                if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                    self.model = joblib.load(self.model_path)
                    self.vectorizer = joblib.load(self.vectorizer_path)
                    loaded = True
            except Exception as e:
                print(f"Error loading model from disk: {e}")

        if not loaded:
            # Initialize and train with default data
            self._initialize_model()
            self._train_with_defaults()

    def _initialize_model(self):
        """Initialize a new ML model"""
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
        self.vectorizer = None

    def _train_with_defaults(self):
        """Train the model with default training data, supplemented by DB data if available"""
        training_data = list(DEFAULT_TRAINING_DATA)

        # Try to load additional training data from database
        try:
            from .models import ChatbotTrainingData
            db_data = ChatbotTrainingData.objects.all()
            if db_data.exists():
                training_data.extend([(item.user_message, item.intent) for item in db_data])
        except Exception:
            pass  # Database unavailable, use defaults only

        self.train(training_data)

    def train(self, training_data):
        """
        Train the model on provided training data

        Args:
            training_data: List of tuples (user_message, intent)
        """
        if not training_data or len(training_data) == 0:
            return False

        messages = [item[0].lower().strip() for item in training_data]
        intents = [item[1] for item in training_data]

        try:
            self.model.fit(messages, intents)
            self._save_model()
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    def predict_intent(self, user_message, conversation_history=None):
        """
        Predict the intent of a user message with context awareness
        """
        if not self.model:
            return 'default'

        try:
            cleaned_message = user_message.lower().strip()

            suraj_keywords = ['suraj', 'kharal', 'suraj kharal', 'him', 'his', 'he']
            is_about_suraj = any(keyword in cleaned_message for keyword in suraj_keywords)

            if conversation_history and len(conversation_history) > 0:
                recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
                context_text = " ".join([msg.get('message', '') for msg in recent_messages if isinstance(msg, dict)])
                enhanced_message = f"{context_text} {cleaned_message}".strip()
            else:
                enhanced_message = cleaned_message

            if is_about_suraj and any(word in cleaned_message for word in ['who', 'what', 'tell', 'about', 'know']):
                if not any(word in cleaned_message for word in ['skill', 'experience', 'contact', 'email', 'phone']):
                    return 'about'

            intent = self.model.predict([enhanced_message])[0]

            probabilities = self.model.predict_proba([enhanced_message])[0]
            max_probability = max(probabilities)

            if max_probability < 0.3:
                return 'default'

            return intent
        except Exception as e:
            print(f"Error predicting intent: {e}")
            return 'default'

    def predict_with_context(self, user_message, conversation_state=None, conversation_history=None):
        """
        Enhanced prediction that considers conversation state and history
        """
        if not self.model:
            return {
                'intent': 'default',
                'confidence': 0.0,
                'actions': []
            }

        try:
            cleaned_message = user_message.lower().strip()

            if conversation_state == 'linkedin_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {'intent': 'linkedin_yes', 'confidence': 1.0, 'actions': ['open_linkedin']}
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'linkedin_no', 'confidence': 1.0, 'actions': ['next_question']}

            elif conversation_state == 'github_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {'intent': 'github_yes', 'confidence': 1.0, 'actions': ['open_github']}
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'github_no', 'confidence': 1.0, 'actions': ['next_question']}

            elif conversation_state == 'email_question':
                if any(word in cleaned_message for word in ['yes', 'y', 'sure', 'ok', 'okay', 'send']):
                    return {'intent': 'email_yes', 'confidence': 1.0, 'actions': ['open_email']}
                elif any(word in cleaned_message for word in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'email_no', 'confidence': 1.0, 'actions': ['end_greeting']}

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

    def get_similar_messages(self, user_message, training_tuples, top_n=3):
        """
        Find similar messages from training data using TF-IDF similarity
        """
        if not training_tuples or len(training_tuples) == 0:
            return []

        try:
            messages = [item[0].lower().strip() for item in training_tuples]
            messages.append(user_message.lower().strip())

            vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True
            )

            tfidf_matrix = vectorizer.fit_transform(messages)

            user_vector = tfidf_matrix[-1]
            training_vectors = tfidf_matrix[:-1]

            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(user_vector, training_vectors)[0]

            top_indices = np.argsort(similarities)[-top_n:][::-1]

            similar_messages = []
            for idx in top_indices:
                if similarities[idx] > 0.1:
                    similar_messages.append({
                        'message': training_tuples[idx][0],
                        'intent': training_tuples[idx][1],
                        'response': training_tuples[idx][2],
                        'similarity': float(similarities[idx])
                    })

            return similar_messages
        except Exception as e:
            print(f"Error finding similar messages: {e}")
            return []

    def _save_model(self):
        """Save the trained model to disk (local only, skip on serverless)"""
        if self.is_serverless:
            return
        try:
            import joblib
            joblib.dump(self.model, self.model_path)
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

        data = [(item.user_message, item.intent) for item in training_data]

        return self.train(data)

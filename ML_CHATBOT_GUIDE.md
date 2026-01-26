# ML Chatbot Setup Guide

## Overview
The chatbot has been upgraded from simple keyword matching to a Machine Learning-based system that learns from training data. The ML model uses:
- **TF-IDF Vectorization** for text processing
- **Naive Bayes Classifier** for intent classification
- **Cosine Similarity** for finding similar messages

## Features
- 🤖 **ML-based Intent Classification**: Predicts user intent using trained model
- 📚 **Training Data Management**: Add/edit training examples through Django Admin
- 🔄 **Automatic Retraining**: Model retrains automatically when training data changes
- 🎯 **Similarity Matching**: Finds similar messages from training data for better responses

## Setup Instructions

### 1. Install Dependencies
Install the new ML dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- `scikit-learn==1.3.2` - Machine learning library
- `numpy==1.24.3` - Numerical computing
- `joblib==1.3.2` - Model serialization

### 2. Create Database Migration
Create and apply migrations for the new `ChatbotTrainingData` model:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Populate Initial Training Data
Run the management command to populate initial training data:
```bash
python manage.py populate_training_data
```

This command will:
- Create training examples for common intents (greeting, about, skills, experience, contact, availability, job_offer)
- Automatically train the ML model with this data
- Save the trained model to `crudapp/ml_models/chatbot_model.pkl`

### 4. Test the Chatbot
1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Visit your portfolio page
3. Open the chatbot and try different questions
4. The chatbot will now use ML to predict intent and generate responses

## How It Works

### Intent Classification
The ML model predicts one of these intents:
- `greeting` - Greetings and salutations
- `about` - Questions about background/information
- `skills` - Questions about skills and technologies
- `experience` - Questions about work experience
- `contact` - Questions about contact information
- `availability` - Questions about job availability
- `job_offer` - Job offer submissions
- `default` - General/default responses

### Response Generation
1. **ML Prediction**: User message is processed through the trained model to predict intent
2. **Similarity Matching**: System finds similar messages from training data using TF-IDF cosine similarity
3. **Response Selection**: 
   - If a similar message is found (similarity > 0.5), use its response
   - Otherwise, generate response based on predicted intent

## Managing Training Data

### Through Django Admin
1. Go to Django Admin: http://127.0.0.1:8000/admin/
2. Click on "Chatbot Training Data"
3. Add new training examples:
   - **User Message**: Example user question/message
   - **Intent**: Select the intent category
   - **Response**: The response the chatbot should give
4. The model will automatically retrain when you save

### Adding Training Data Programmatically
```python
from crudapp.models import ChatbotTrainingData

ChatbotTrainingData.objects.create(
    user_message="what programming languages do you know?",
    intent="skills",
    response="I have experience with Python, JavaScript, and Java."
)
```

### Retraining the Model
The model automatically retrains when:
- New training data is added
- Training data is updated
- Training data is deleted

You can also manually retrain:
1. In Django Admin, select training data entries
2. Choose "Retrain ML model with all training data" from the Actions dropdown
3. Click "Go"

Or programmatically:
```python
from crudapp.ml_chatbot import MLChatbotService

ml_chatbot = MLChatbotService()
ml_chatbot.retrain_from_database()
```

## Improving the Chatbot

### Tips for Better Training Data
1. **Variety**: Add multiple ways users might ask the same question
   - "what are your skills?"
   - "tell me about your expertise"
   - "what technologies do you know?"

2. **Context**: Include context-specific variations
   - "hi" (casual)
   - "hello" (formal)
   - "good morning" (time-specific)

3. **Common Misspellings**: Include common typos and variations
   - "skils" → "skills"
   - "experiance" → "experience"

4. **Natural Language**: Use natural, conversational examples
   - "can you tell me about yourself?"
   - "what's your background?"

### Monitoring Performance
The chatbot response includes the predicted intent (for debugging):
```json
{
    "response": "...",
    "action": null,
    "intent": "skills"
}
```

Check the Django console/logs for:
- Model training status
- Prediction errors
- Similarity scores

## Troubleshooting

### Model Not Training?
- Ensure you have training data: `ChatbotTrainingData.objects.count() > 0`
- Check file permissions for `crudapp/ml_models/` directory
- Check Django logs for errors

### Poor Predictions?
- Add more training data for the problematic intent
- Ensure training data covers various phrasings
- Retrain the model after adding new data

### Model File Issues?
- Delete `crudapp/ml_models/chatbot_model.pkl` and `vectorizer.pkl`
- Run `populate_training_data` command again
- The model will be recreated automatically

## Technical Details

### Model Architecture
- **Vectorizer**: TF-IDF with n-grams (1-2), max 5000 features
- **Classifier**: Multinomial Naive Bayes with alpha=1.0
- **Similarity**: Cosine similarity on TF-IDF vectors

### Model Storage
- Trained models are saved in `crudapp/ml_models/`
- `chatbot_model.pkl` - Full pipeline (vectorizer + classifier)
- `vectorizer.pkl` - TF-IDF vectorizer (for similarity matching)

### Performance
- Training time: ~1-2 seconds for 50-100 examples
- Prediction time: <100ms per message
- Model size: ~500KB-2MB depending on training data

## Next Steps

### Advanced Improvements
1. **Neural Networks**: Upgrade to a neural network model (LSTM/Transformer)
2. **Context Awareness**: Add conversation history tracking
3. **Confidence Thresholds**: Adjust minimum confidence for predictions
4. **Multi-label Classification**: Support multiple intents per message
5. **Entity Extraction**: Extract specific information (names, dates, etc.)

### Integration Options
- **OpenAI API**: Use GPT models for more advanced responses
- **Rasa**: Full conversational AI framework
- **Dialogflow**: Google's conversational AI platform

## Support
For issues or questions:
1. Check Django logs for errors
2. Verify training data exists and is correct
3. Ensure all dependencies are installed
4. Try retraining the model manually

# Quick Start Guide

## ✅ What You Need to Do

### Step 1: Install Dependencies (REQUIRED)
The new ML libraries need to be installed:
```bash
cd django_crud_project
pip install -r requirements.txt
```

**Why?** You need:
- `scikit-learn` - For ML model
- `numpy` - For numerical operations
- `joblib` - For saving/loading models

### Step 2: Run Migrations (REQUIRED)
Even though migration files exist, you need to apply them:
```bash
python manage.py migrate
```

**Why?** This creates the database tables for:
- `ChatbotTrainingData` - Stores training examples
- `ChatbotConversation` - Stores conversation sessions

### Step 3: Populate Training Data (REQUIRED)
Train the ML model with initial data:
```bash
python manage.py populate_training_data
```

**Why?** This:
- Creates ~50+ training examples
- Trains the ML model
- Saves model to `crudapp/ml_models/`

### Step 4: Verify PersonalInfo (IMPORTANT)
Go to: http://127.0.0.1:8000/admin/
- Check if `PersonalInfo` exists
- If not, create one with your information

### Step 5: Run Server
```bash
python manage.py runserver
```

## 🚨 Can You Skip Any Steps?

**NO** - All steps are required:
- ❌ **Can't skip dependencies** - Code will crash without scikit-learn
- ❌ **Can't skip migrations** - Database tables won't exist
- ❌ **Can't skip training data** - ML model won't work
- ⚠️ **Can skip PersonalInfo** - But chatbot will use default values

## ⚡ Quick Command Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Populate training data
python manage.py populate_training_data

# 4. Start server
python manage.py runserver
```

## 🔍 How to Check If Already Done

### Check Dependencies
```bash
pip list | grep scikit-learn
# Should show: scikit-learn 1.3.2
```

### Check Migrations
```bash
python manage.py showmigrations crudapp
# Should show all migrations as [X] (applied)
```

### Check Training Data
```bash
python manage.py shell
>>> from crudapp.models import ChatbotTrainingData
>>> ChatbotTrainingData.objects.count()
# Should be > 0
```

### Check Model File
```bash
ls crudapp/ml_models/chatbot_model.pkl
# File should exist
```

## 🎯 Minimum Requirements to Run

Before running `python manage.py runserver`, ensure:
1. ✅ Dependencies installed (`pip install -r requirements.txt`)
2. ✅ Migrations applied (`python manage.py migrate`)
3. ✅ Training data populated (`python manage.py populate_training_data`)

## 💡 Pro Tip

Run this one-liner to check everything:
```bash
python manage.py shell -c "from crudapp.models import ChatbotTrainingData, ChatbotConversation; from crudapp.ml_chatbot import MLChatbotService; print('Training data:', ChatbotTrainingData.objects.count()); print('Model exists:', MLChatbotService().model is not None)"
```

If it runs without errors, you're good to go! 🎉

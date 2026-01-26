# Git Commit Instructions

## Steps to Commit Your Changes

### Step 1: Unstage Unnecessary Files
Remove cache files, database, and model files from staging:

```bash
cd django_crud_project
git restore --staged crudapp/__pycache__/*
git restore --staged crudapp/migrations/__pycache__/*
git restore --staged crudapp/management/__pycache__/*
git restore --staged crudapp/management/commands/__pycache__/*
git restore --staged db.sqlite3
git restore --staged crudapp/ml_models/*.pkl
```

**Why?** These files shouldn't be committed:
- `__pycache__/` - Python cache files (auto-generated)
- `db.sqlite3` - Database file (contains local data)
- `*.pkl` - ML model files (large, auto-generated)

### Step 2: Verify What Will Be Committed
```bash
git status
```

You should see only:
- ✅ Source code files (.py)
- ✅ Templates (.html)
- ✅ Migrations (.py in migrations/)
- ✅ Documentation (.md)
- ✅ Configuration files (requirements.txt, etc.)
- ❌ NO __pycache__ files
- ❌ NO db.sqlite3
- ❌ NO .pkl files

### Step 3: Commit with Descriptive Message
```bash
git commit -m "feat: Add ML-based chatbot with context awareness and varied responses

- Implement ML chatbot using scikit-learn (TF-IDF + Naive Bayes)
- Add context-aware conversation management with session tracking
- Create varied response generator for natural conversations
- Add initial greeting flow with LinkedIn/GitHub/Email options
- Implement 4-second inactivity timeout with helpful prompts
- Add training data management via Django admin
- Create conversation state management system
- Enhance question detection for Suraj Kharal queries
- Add database-driven responses using PersonalInfo model
- Include comprehensive documentation and setup guides

New features:
- ML-based intent classification
- Conversation history tracking
- Varied response generation
- Initial greeting flow
- Inactivity timeout
- Session persistence
- Admin interface for training data"
```

### Step 4: (Optional) Push to Remote
```bash
git push origin main
```

## Alternative: Simpler Commit Message

If you prefer a shorter message:

```bash
git commit -m "feat: Add ML-based chatbot with context awareness

- ML chatbot with scikit-learn
- Context-aware conversations
- Varied response generation
- Initial greeting flow
- Session management
- Training data admin interface"
```

## Files That Should Be Committed

✅ **Source Code:**
- `crudapp/ml_chatbot.py`
- `crudapp/conversation_manager.py`
- `crudapp/response_generator.py`
- `crudapp/models.py` (updated)
- `crudapp/views.py` (updated)
- `crudapp/admin.py` (updated)
- `crudapp/forms.py` (updated)
- `crudapp/urls.py` (updated)

✅ **Templates:**
- `crudapp/templates/crudapp/Suraj.html` (updated)

✅ **Migrations:**
- `crudapp/migrations/0002_joboffer_personalinfo.py`
- `crudapp/migrations/0003_chatbottrainingdata.py`
- `crudapp/migrations/0004_chatbotconversation.py`

✅ **Management Commands:**
- `crudapp/management/commands/populate_training_data.py`

✅ **Configuration:**
- `requirements.txt` (updated)
- `.gitignore` (updated)

✅ **Documentation:**
- All `.md` files

✅ **ML Models Directory:**
- `crudapp/ml_models/.gitkeep`
- `crudapp/ml_models/__init__.py`
- (But NOT the .pkl files)

## Files That Should NOT Be Committed

❌ `crudapp/__pycache__/` - Python cache
❌ `crudapp/migrations/__pycache__/` - Migration cache
❌ `crudapp/management/__pycache__/` - Management cache
❌ `db.sqlite3` - Local database
❌ `crudapp/ml_models/*.pkl` - ML model files (large, auto-generated)

## Troubleshooting

### If git restore fails:
The files might already be tracked. Remove them from git:
```bash
git rm --cached -r crudapp/__pycache__
git rm --cached db.sqlite3
git rm --cached crudapp/ml_models/*.pkl
```

### If .gitignore doesn't work:
Make sure the files aren't already tracked:
```bash
git rm --cached <file>
```

Then add to .gitignore and commit.

## Quick One-Liner (After Unstaging)

```bash
git commit -m "feat: Add ML-based chatbot with context awareness and varied responses"
```

# Quick Commit Guide

## ⚠️ Important: Unstage Unnecessary Files First!

Before committing, remove these files from staging:

```bash
cd django_crud_project

# Unstage cache files
git restore --staged crudapp/__pycache__/*
git restore --staged crudapp/migrations/__pycache__/*
git restore --staged crudapp/management/__pycache__/*
git restore --staged crudapp/management/commands/__pycache__/*

# Unstage database and model files
git restore --staged db.sqlite3
git restore --staged crudapp/ml_models/*.pkl
```

## Then Commit

```bash
git commit -m "feat: Add ML-based chatbot with context awareness and varied responses

- ML chatbot using scikit-learn (TF-IDF + Naive Bayes)
- Context-aware conversation management
- Varied response generator
- Initial greeting flow with LinkedIn/GitHub/Email
- 4-second inactivity timeout
- Training data management via admin
- Session persistence
- Enhanced question detection"
```

## Or If You Want to Commit Everything (Not Recommended)

If you just want to commit everything as-is:

```bash
git commit -m "feat: Add ML-based chatbot with context awareness and varied responses"
```

**Note:** This will include cache files and database, which isn't ideal but will work.

## Push to Remote (Optional)

```bash
git push origin main
```

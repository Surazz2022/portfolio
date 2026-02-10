# Suraj Kharal - Portfolio & AI Chatbot

A personal portfolio website built with **Django** and deployed on **Vercel**, featuring an ML-powered chatbot assistant that answers questions about my skills, experience, and availability.

**Live:** [surajkharal.vercel.app](https://surajkharal.vercel.app/)

## Features

- **AI Chatbot** - ML-based assistant (scikit-learn + NaiveBayes) that answers recruiter questions about skills, experience, contact info, and availability
- **Job Offer Submission** - Recruiters can submit job offers directly through the chatbot
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Serverless Ready** - Runs on Vercel with in-memory sessions and cookie-based storage

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.1, Python 3.12 |
| ML | scikit-learn, TF-IDF + MultinomialNB |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Vercel (Serverless) |
| Database | SQLite (local) / In-memory (Vercel) |

## Project Structure

```
django_crud_project/
├── crudapp/
│   ├── ml_chatbot.py           # ML model for intent classification
│   ├── conversation_manager.py # Conversation state & flow management
│   ├── response_generator.py   # Response generation per intent
│   ├── views.py                # API endpoints
│   ├── models.py               # Django models
│   └── templates/crudapp/
│       └── Suraj.html          # Portfolio page + chatbot widget
├── django_crud_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── vercel.json                 # Vercel deployment config
├── requirements.txt
└── manage.py
```

## Local Setup

```bash
# Clone
git clone git@github.com:Surazz2022/portfolio.git
cd portfolio

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Visit `http://localhost:8000/`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Portfolio page |
| `/api/chatbot/` | POST | Chatbot interaction |
| `/api/job-offer/` | POST | Submit a job offer |

## Chatbot Intents

The chatbot recognizes these intents and responds with relevant information:

- **greeting** - Hello, hi, hey
- **about** - Who is Suraj, tell me about him
- **skills** - What are his skills, technologies
- **experience** - Work history, past jobs
- **contact** - Email, phone, how to reach
- **availability** - Is he open to work
- **job_offer** - I want to hire, job opportunity

## Author

**Suraj Kharal** - AI/ML Engineer

- [LinkedIn](https://www.linkedin.com/in/suraj-kharal-baa9271b1/)
- [GitHub](https://github.com/Surazz2022)
- Email: surz.khl49@gmail.com

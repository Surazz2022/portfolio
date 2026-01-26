# Chatbot Agent Setup Guide

## Overview
This chatbot agent allows recruiters to interact with your portfolio, learn about you, and autonomously submit job offers.

## Features
- 🤖 AI-powered chatbot that answers questions about your skills, experience, and availability
- 📝 Job offer submission form integrated into the chat
- 💾 All job offers are stored in the database for review
- 🎨 Modern, responsive UI that matches your portfolio design

## Setup Instructions

### 1. Run Migrations
First, create and apply database migrations for the new models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Add Your Personal Information
You have two options:

#### Option A: Using Django Admin (Recommended)
1. Create a superuser if you haven't already:
   ```bash
   python manage.py createsuperuser
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Go to http://127.0.0.1:8000/admin/
4. Login with your superuser credentials
5. Click on "Personal Informations" → "Add Personal Information"
6. Fill in all your details:
   - Full Name
   - Title/Position
   - Email
   - Phone
   - Location
   - LinkedIn URL (optional)
   - GitHub URL (optional)
   - Bio
   - Skills Summary (comma-separated)
   - Experience Summary
   - Availability Status
   - Preferred Roles
   - Salary Expectation (optional)
   - Work Preference (Remote/On-site/Hybrid/Any)

#### Option B: Using Django Shell
```bash
python manage.py shell
```

Then run:
```python
from crudapp.models import PersonalInfo

PersonalInfo.objects.create(
    full_name="Suraj Kharal",
    title="Junior Machine Learning Engineer & Data Analyst",
    email="surz.khl49@gmail.com",
    phone="+977-9869407702",
    location="Devdaha 07, Rupandehi, Nepal",
    linkedin_url="https://www.linkedin.com/in/suraj-kharal-baa9271b1/",
    github_url="https://github.com/Surazz2022",
    bio="I am a motivated data professional with a good foundation in machine learning, statistics, and python programming. I have a good working experience on time series datasets and building end to end data pipelines for automating the flow of data and building the predictive models.",
    skills_summary="Python, Machine Learning, Data Analysis, LSTM, ARIMA, Time Series Analysis, Data Pipelines, Django, Flask, FastAPI",
    experience_summary="Junior ML Engineer at CognifyNow (Apr 2025 - Sept 2025), Junior Data Analyst at NepseTrading (Nov 2024 - Apr 2025)",
    availability="Available for opportunities",
    preferred_roles="Machine Learning Engineer, Data Scientist, Data Analyst, ML Engineer",
    work_preference="any"
)
```

### 3. Test the Chatbot
1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Visit your portfolio page (usually http://127.0.0.1:8000/)
3. Look for the chatbot button in the bottom-right corner
4. Click it to open the chat interface
5. Try asking questions like:
   - "Tell me about Suraj"
   - "What are his skills?"
   - "Is he available for opportunities?"
   - "I want to submit a job offer"

### 4. View Job Offers
All job offers submitted by recruiters will be stored in the database. To view them:

1. Go to Django Admin: http://127.0.0.1:8000/admin/
2. Click on "Job Offers"
3. You'll see all submitted offers with their status
4. You can update the status (Pending → Reviewed → Accepted/Declined)

## How It Works

### Chatbot Flow
1. **Greeting**: The chatbot greets visitors and offers help
2. **Information Queries**: Answers questions about:
   - Skills and expertise
   - Work experience
   - Contact information
   - Availability
   - Preferred roles

3. **Job Offer Flow**: When a recruiter mentions job offers:
   - The chatbot guides them through the process
   - Offers to show a detailed form
   - Collects all necessary information
   - Submits the offer to the database

### API Endpoints
- `POST /api/chatbot/` - Handles chatbot interactions
- `POST /api/job-offer/` - Submits job offers

## Customization

### Updating Chatbot Responses
Edit the `chatbot_interact` function in `crudapp/views.py` to customize responses.

### Styling
The chatbot styles are in `Suraj.html` within the `<style>` section. Look for "Chatbot Widget Styles" comments.

### Adding More Features
You can enhance the chatbot by:
- Integrating with OpenAI API for more intelligent responses
- Adding email notifications when job offers are submitted
- Creating a dashboard to view analytics
- Adding more conversation flows

## Notes
- The chatbot uses keyword matching for responses. For production, consider integrating with an AI service like OpenAI.
- CSRF protection is disabled for API endpoints (`@csrf_exempt`). For production, implement proper CSRF handling.
- Job offers are stored with status "pending" by default. Update them in the admin panel.

## Troubleshooting

### Chatbot not appearing?
- Check browser console for JavaScript errors
- Ensure Django server is running
- Verify URLs are correctly configured

### Job offers not submitting?
- Check browser console for errors
- Verify CSRF token is being sent (check Network tab)
- Check Django server logs for errors

### Personal info not showing?
- Ensure you've created a PersonalInfo entry in the database
- The chatbot will use default values if no PersonalInfo exists

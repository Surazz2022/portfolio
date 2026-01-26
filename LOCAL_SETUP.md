# Local Development Setup Guide

## Quick Start

### Option 1: Using PowerShell Script (Recommended)
1. Open PowerShell in the `django_crud_project` directory
2. Run:
   ```powershell
   .\run_local.ps1
   ```

### Option 2: Using Batch File
1. Double-click `run_local.bat` or run it from command prompt

### Option 3: Manual Steps

#### Step 1: Activate Virtual Environment
```powershell
# From portfolio directory
.\venv\Scripts\Activate.ps1

# Navigate to project directory
cd django_crud_project
```

#### Step 2: Run Migrations
```powershell
python manage.py migrate
```

#### Step 3: Create Superuser (if you haven't already)
```powershell
python manage.py createsuperuser
```
Follow the prompts to create an admin user.

#### Step 4: Start Development Server
```powershell
python manage.py runserver
```

The server will start at: **http://127.0.0.1:8000/**

---

## Testing the Chatbot

### 1. Add Your Personal Information
1. Go to: http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Click on **"Personal Informations"** → **"Add Personal Information"**
4. Fill in all your details (see CHATBOT_SETUP.md for details)

### 2. Test the Portfolio Page
1. Visit: http://127.0.0.1:8000/
2. Look for the chatbot button in the bottom-right corner (💬 icon)
3. Click it to open the chat interface

### 3. Test Chatbot Interactions
Try asking:
- "Hello" or "Hi"
- "Tell me about Suraj"
- "What are his skills?"
- "Is he available?"
- "I want to submit a job offer"

### 4. Test Job Offer Submission
1. In the chatbot, say: "I want to submit a job offer"
2. The chatbot will guide you through the process
3. Fill out the form with test data
4. Submit the offer
5. Check the admin panel to see the submitted offer

---

## Viewing Job Offers

1. Go to: http://127.0.0.1:8000/admin/
2. Click on **"Job Offers"**
3. You'll see all submitted offers
4. You can update their status (Pending → Reviewed → Accepted/Declined)

---

## Troubleshooting

### Port Already in Use
If port 8000 is busy, use a different port:
```powershell
python manage.py runserver 8001
```

### Migration Errors
If you get migration errors:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Virtual Environment Not Found
Make sure you're in the portfolio directory and the venv folder exists:
```powershell
# From portfolio directory
.\venv\Scripts\Activate.ps1
```

### Import Errors
Make sure Django is installed in your virtual environment:
```powershell
pip install -r requirements.txt
```

### Chatbot Not Appearing
1. Check browser console (F12) for JavaScript errors
2. Make sure the server is running
3. Hard refresh the page (Ctrl+F5)
4. Check that Suraj.html was saved correctly

---

## Next Steps After Local Testing

Once everything works locally:
1. Test all chatbot features thoroughly
2. Add your complete personal information
3. Test job offer submission flow
4. Review submitted offers in admin panel
5. Then proceed with deployment

---

## Useful Commands

```powershell
# Create superuser
python manage.py createsuperuser

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Run server on specific port
python manage.py runserver 8001

# Open Django shell
python manage.py shell
```

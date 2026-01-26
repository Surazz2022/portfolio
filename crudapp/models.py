# django_crud_project/crudapp/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PersonalInfo(models.Model):
    """Model to store personal information for the agent"""
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    bio = models.TextField()
    skills_summary = models.TextField(help_text="Comma-separated list of key skills")
    experience_summary = models.TextField(help_text="Brief summary of experience")
    availability = models.CharField(max_length=100, default="Available for opportunities")
    preferred_roles = models.TextField(help_text="Preferred job roles/positions")
    salary_expectation = models.CharField(max_length=100, blank=True, null=True)
    work_preference = models.CharField(max_length=50, choices=[
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('any', 'Any')
    ], default='any')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Personal Information"

    def __str__(self):
        return self.full_name


class JobOffer(models.Model):
    """Model to store job offers from recruiters"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    recruiter_name = models.CharField(max_length=200)
    recruiter_email = models.EmailField()
    recruiter_company = models.CharField(max_length=200)
    recruiter_phone = models.CharField(max_length=20, blank=True, null=True)
    
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_description = models.TextField()
    location = models.CharField(max_length=200)
    work_type = models.CharField(max_length=50, choices=[
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
    ], default='remote')
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    start_date = models.CharField(max_length=100, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.job_title} at {self.company_name} - {self.recruiter_name}"


class ChatbotTrainingData(models.Model):
    """Model to store training data for the ML chatbot"""
    INTENT_CHOICES = [
        ('greeting', 'Greeting'),
        ('about', 'About/Information'),
        ('skills', 'Skills'),
        ('experience', 'Experience'),
        ('contact', 'Contact Info'),
        ('availability', 'Availability'),
        ('job_offer', 'Job Offer'),
        ('default', 'Default/General'),
    ]
    
    user_message = models.TextField(help_text="Example user message/question")
    intent = models.CharField(max_length=50, choices=INTENT_CHOICES, help_text="Intent category")
    response = models.TextField(help_text="Expected response for this message")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['intent', 'created_at']
        verbose_name_plural = "Chatbot Training Data"
    
    def __str__(self):
        return f"{self.intent}: {self.user_message[:50]}..."


class ChatbotConversation(models.Model):
    """Model to store conversation state and context"""
    session_id = models.CharField(max_length=255, unique=True, help_text="Unique session identifier")
    conversation_state = models.CharField(
        max_length=50,
        default='initial',
        choices=[
            ('initial', 'Initial Greeting'),
            ('linkedin_question', 'LinkedIn Question'),
            ('github_question', 'GitHub Question'),
            ('email_question', 'Email Question'),
            ('normal', 'Normal Conversation'),
            ('job_offer_flow', 'Job Offer Flow'),
        ]
    )
    conversation_history = models.JSONField(default=list, help_text="List of conversation messages")
    context = models.JSONField(default=dict, help_text="Additional context data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Session {self.session_id[:8]}... - {self.conversation_state}"
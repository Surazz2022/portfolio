# django_crud_project/crudapp/forms.py
from django import forms
from .models import Item, JobOffer

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']


class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = [
            'recruiter_name', 'recruiter_email', 'recruiter_company', 'recruiter_phone',
            'job_title', 'company_name', 'job_description', 'location', 'work_type',
            'salary_range', 'benefits', 'start_date', 'additional_info'
        ]
        widgets = {
            'recruiter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'recruiter_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@company.com'
            }),
            'recruiter_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your company name'
            }),
            'recruiter_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Machine Learning Engineer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the role and responsibilities...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Remote, New York, Hybrid'
            }),
            'work_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'salary_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $80,000 - $120,000'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Health insurance, 401k, etc.'
            }),
            'start_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., ASAP, January 2025'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional information...'
            }),
        }
"""
Management command to populate initial training data for the ML chatbot
"""
from django.core.management.base import BaseCommand
from crudapp.models import ChatbotTrainingData, PersonalInfo
from crudapp.ml_chatbot import MLChatbotService


class Command(BaseCommand):
    help = 'Populate initial training data for the ML chatbot'

    def handle(self, *args, **options):
        # Get personal info for dynamic responses
        personal_info = PersonalInfo.objects.first()
        
        # Default info if no personal info exists
        if personal_info:
            name = personal_info.full_name
            title = personal_info.title
            email = personal_info.email
            phone = personal_info.phone
            location = personal_info.location
            bio = personal_info.bio
            skills = personal_info.skills_summary
            experience = personal_info.experience_summary
            availability = personal_info.availability
            preferred_roles = personal_info.preferred_roles
        else:
            name = 'Suraj Kharal'
            title = 'Junior Machine Learning Engineer & Data Analyst'
            email = 'surz.khl49@gmail.com'
            phone = '+977-9869407702'
            location = 'Devdaha 07, Rupandehi, Nepal'
            bio = 'I am a motivated data professional with a good foundation in machine learning, statistics, and python programming.'
            skills = 'Python, Machine Learning, Data Analysis, LSTM, ARIMA, Time Series Analysis, Data Pipelines'
            experience = 'Junior ML Engineer at CognifyNow, Junior Data Analyst at NepseTrading'
            availability = 'Available for opportunities'
            preferred_roles = 'Machine Learning Engineer, Data Scientist, Data Analyst'

        # Initial training data
        training_data = [
            # Greetings
            ('hi', 'greeting', f"Hello! I'm an AI assistant representing {name}. How can I help you today? Would you like to know more about {name} or submit a job offer?"),
            ('hello', 'greeting', f"Hello! I'm an AI assistant representing {name}. How can I help you today? Would you like to know more about {name} or submit a job offer?"),
            ('hey', 'greeting', f"Hello! I'm an AI assistant representing {name}. How can I help you today? Would you like to know more about {name} or submit a job offer?"),
            ('greetings', 'greeting', f"Hello! I'm an AI assistant representing {name}. How can I help you today? Would you like to know more about {name} or submit a job offer?"),
            ('good morning', 'greeting', f"Good morning! I'm an AI assistant representing {name}. How can I help you today?"),
            ('good afternoon', 'greeting', f"Good afternoon! I'm an AI assistant representing {name}. How can I help you today?"),
            ('good evening', 'greeting', f"Good evening! I'm an AI assistant representing {name}. How can I help you today?"),
            
            # About/Information - More variations about Suraj
            ('tell me about yourself', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('who are you', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('what do you do', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('tell me about', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('information about', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('background', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('introduce yourself', 'about', f"{bio}\n\n{name} is a {title} with expertise in {skills}."),
            ('who is suraj', 'about', f"{name} is a {title}. {bio}"),
            ('who is suraj kharal', 'about', f"{name} is a {title} based in {location}. {bio}"),
            ('tell me about suraj', 'about', f"{name} is a {title}. {bio} He specializes in {skills}."),
            ('about suraj kharal', 'about', f"{name} is a {title}. {bio} His experience includes {experience}."),
            ('who is he', 'about', f"{name} is a {title}. {bio}"),
            ('tell me about him', 'about', f"{name} is a {title}. {bio} He has expertise in {skills}."),
            ('what do you know about suraj', 'about', f"{name} is a {title}. {bio} His professional background includes {experience}."),
            
            # Skills
            ('what are your skills', 'skills', f"{name} has experience with: {skills}"),
            ('what skills do you have', 'skills', f"{name} has experience with: {skills}"),
            ('what technologies do you know', 'skills', f"{name} has experience with: {skills}"),
            ('what is your tech stack', 'skills', f"{name} has experience with: {skills}"),
            ('expertise', 'skills', f"{name} has experience with: {skills}"),
            ('technologies', 'skills', f"{name} has experience with: {skills}"),
            ('programming languages', 'skills', f"{name} has experience with: {skills}"),
            
            # Experience
            ('what is your experience', 'experience', f"Experience: {experience}"),
            ('work experience', 'experience', f"Experience: {experience}"),
            ('career', 'experience', f"Experience: {experience}"),
            ('work history', 'experience', f"Experience: {experience}"),
            ('previous jobs', 'experience', f"Experience: {experience}"),
            ('where have you worked', 'experience', f"Experience: {experience}"),
            
            # Contact
            ('contact information', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            ('how to contact', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            ('email', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            ('phone number', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            ('reach out', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            ('get in touch', 'contact', f"Contact Information:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}"),
            
            # Availability
            ('are you available', 'availability', f"{availability}. {name} is interested in roles like: {preferred_roles}"),
            ('availability', 'availability', f"{availability}. {name} is interested in roles like: {preferred_roles}"),
            ('are you looking for work', 'availability', f"{availability}. {name} is interested in roles like: {preferred_roles}"),
            ('open to opportunities', 'availability', f"{availability}. {name} is interested in roles like: {preferred_roles}"),
            ('looking for jobs', 'availability', f"{availability}. {name} is interested in roles like: {preferred_roles}"),
            
            # Job Offer
            ('job offer', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            ('i have a job offer', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            ('want to hire', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            ('recruiting', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            ('position available', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            ('opportunity', 'job_offer', "Great! I'd be happy to help you submit a job offer. Would you like me to guide you through the process? Just say 'yes' or 'submit offer' to get started!"),
            
            # Default/General
            ('help', 'default', f"I'm here to help! You can ask me about:\n• {name}'s skills and experience\n• Contact information\n• Availability for opportunities\n• Submitting a job offer\n\nWhat would you like to know?"),
            ('what can you do', 'default', f"I'm here to help! You can ask me about:\n• {name}'s skills and experience\n• Contact information\n• Availability for opportunities\n• Submitting a job offer\n\nWhat would you like to know?"),
        ]
        
        # Clear existing training data (optional - comment out if you want to keep existing data)
        # ChatbotTrainingData.objects.all().delete()
        
        # Create training data entries
        created_count = 0
        updated_count = 0
        
        for user_msg, intent, response in training_data:
            obj, created = ChatbotTrainingData.objects.get_or_create(
                user_message=user_msg,
                defaults={
                    'intent': intent,
                    'response': response
                }
            )
            if created:
                created_count += 1
            else:
                # Update if exists
                obj.intent = intent
                obj.response = response
                obj.save()
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated training data: {created_count} created, {updated_count} updated'
            )
        )
        
        # Train the model
        self.stdout.write('Training ML model...')
        ml_chatbot = MLChatbotService()
        success = ml_chatbot.retrain_from_database()
        
        if success:
            self.stdout.write(self.style.SUCCESS('ML model trained successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Failed to train ML model. Check if there is training data.'))

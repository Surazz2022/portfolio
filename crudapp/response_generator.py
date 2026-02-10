"""
Enhanced Response Generator
Generates varied, context-aware responses based on database info and web search
"""
import random
from .models import PersonalInfo


class ResponseGenerator:
    """Generates varied and context-aware responses"""
    
    @staticmethod
    def get_personal_info():
        """Get personal info from database"""
        try:
            return PersonalInfo.objects.first()
        except Exception:
            return None
    
    @staticmethod
    def generate_about_response(personal_info, user_message, context=None):
        """Generate varied about responses based on database info"""
        if not personal_info:
            return "I don't have detailed information available right now. Would you like to know about skills, experience, or contact information?"
        
        name = personal_info.full_name
        title = personal_info.title
        bio = personal_info.bio
        skills = personal_info.skills_summary
        experience = personal_info.experience_summary
        location = personal_info.location
        
        # Check if user is asking specifically about name
        message_lower = user_message.lower()
        
        # More varied and detailed responses
        responses = [
            f"{name} is a {title} based in {location}. {bio}",
            f"Let me introduce {name}. He's a {title} with expertise in {skills.split(',')[0] if skills else 'technology'}. {bio}",
            f"{name} is a {title}. {bio} His professional experience includes {experience}.",
            f"About {name}: He's a {title} who {bio.lower()} He has worked on projects involving {skills}.",
            f"{name} is a {title} from {location}. {bio} He specializes in technologies like {skills}.",
            f"Here's what I know about {name}: He's a {title} with experience in {experience}. {bio}",
        ]
        
        # If asking specifically about the person (with name or pronouns)
        if any(word in message_lower for word in ['who is', 'tell me about', 'about', 'who are you', 'introduce']):
            if any(keyword in message_lower for keyword in ['suraj', 'kharal', 'him', 'his', 'he']):
                return random.choice(responses)
        
        return random.choice(responses)
    
    @staticmethod
    def generate_skills_response(personal_info, user_message, context=None):
        """Generate varied skills responses"""
        if not personal_info:
            return "Skills information is not available. Would you like to know about experience or contact information?"
        
        name = personal_info.full_name
        skills = personal_info.skills_summary
        skills_list = [s.strip() for s in skills.split(',')] if skills else []
        
        responses = [
            f"{name} has expertise in: {skills}",
            f"Here are {name}'s key skills: {skills}",
            f"{name} is proficient in {skills}",
            f"Technical skills include: {skills}",
        ]
        
        # If specific skill mentioned, provide more detail
        message_lower = user_message.lower()
        for skill in skills_list:
            if skill.lower() in message_lower:
                return f"Yes! {name} has experience with {skill}. In fact, {name}'s skills include: {skills}"
        
        return random.choice(responses)
    
    @staticmethod
    def generate_experience_response(personal_info, user_message, context=None):
        """Generate varied experience responses"""
        if not personal_info:
            return "Experience information is not available. Would you like to know about skills or contact information?"
        
        name = personal_info.full_name
        experience = personal_info.experience_summary
        title = personal_info.title
        
        responses = [
            f"{name}'s experience: {experience}",
            f"Here's {name}'s professional background: {experience}",
            f"{name}, a {title}, has the following experience: {experience}",
            f"Professional experience: {experience}",
        ]
        
        return random.choice(responses)
    
    @staticmethod
    def generate_contact_response(personal_info, user_message, context=None):
        """Generate varied contact responses"""
        if not personal_info:
            return "Contact information is not available."
        
        name = personal_info.full_name
        email = personal_info.email
        phone = personal_info.phone
        location = personal_info.location
        linkedin = personal_info.linkedin_url
        github = personal_info.github_url
        
        responses = [
            f"Here's how to reach {name}:\n📧 Email: {email}\n📱 Phone: {phone}\n📍 Location: {location}",
            f"Contact Information:\n📧 {email}\n📱 {phone}\n📍 {location}",
            f"You can contact {name} at:\n📧 {email}\n📱 {phone}\n📍 {location}",
        ]
        
        # Add LinkedIn/GitHub if available
        if linkedin or github:
            response = random.choice(responses)
            if linkedin:
                response += f"\n🔗 LinkedIn: {linkedin}"
            if github:
                response += f"\n💻 GitHub: {github}"
            return response
        
        return random.choice(responses)
    
    @staticmethod
    def generate_availability_response(personal_info, user_message, context=None):
        """Generate varied availability responses"""
        if not personal_info:
            return "Availability information is not available."
        
        name = personal_info.full_name
        availability = personal_info.availability
        preferred_roles = personal_info.preferred_roles
        
        responses = [
            f"{availability}. {name} is interested in roles like: {preferred_roles}",
            f"Great question! {availability}. Preferred positions include: {preferred_roles}",
            f"{name} is {availability.lower()}. Looking for opportunities as: {preferred_roles}",
        ]
        
        return random.choice(responses)
    
    @staticmethod
    def generate_greeting_response(personal_info, user_message, context=None):
        """Generate varied greeting responses"""
        if not personal_info:
            name = "Suraj Kharal"
        else:
            name = personal_info.full_name
        
        responses = [
            f"Hello! 👋 I'm here to help you learn about {name}. What would you like to know?",
            f"Hi there! I can tell you about {name}'s skills, experience, and availability. How can I help?",
            f"Welcome! I'm an AI assistant for {name}. Feel free to ask about skills, experience, or submit a job offer!",
        ]
        
        return random.choice(responses)
    
    @staticmethod
    def generate_default_response(personal_info, user_message, context=None):
        """Generate varied default responses"""
        if not personal_info:
            name = "Suraj Kharal"
        else:
            name = personal_info.full_name
        
        responses = [
            f"I'm here to help! You can ask me about:\n• {name}'s skills and expertise\n• Work experience\n• Contact information\n• Availability for opportunities\n• Submitting a job offer\n\nWhat would you like to know?",
            f"Let me help you! I can provide information about:\n• Skills and technologies\n• Professional experience\n• How to get in touch\n• Job availability\n• Submitting offers\n\nWhat interests you?",
            f"Sure! I can help with:\n• Technical skills\n• Career background\n• Contact details\n• Job opportunities\n• Offer submissions\n\nWhat would you like to explore?",
        ]
        
        return random.choice(responses)
    
    @staticmethod
    def generate_response(intent, personal_info, user_message, context=None):
        """Generate response based on intent with variation"""
        generators = {
            'about': ResponseGenerator.generate_about_response,
            'skills': ResponseGenerator.generate_skills_response,
            'experience': ResponseGenerator.generate_experience_response,
            'contact': ResponseGenerator.generate_contact_response,
            'availability': ResponseGenerator.generate_availability_response,
            'greeting': ResponseGenerator.generate_greeting_response,
            'default': ResponseGenerator.generate_default_response,
        }
        
        generator = generators.get(intent, ResponseGenerator.generate_default_response)
        return generator(personal_info, user_message, context)
    
    @staticmethod
    def enhance_with_web_search(query, personal_info):
        """Enhance response with web search (placeholder for future implementation)"""
        # This can be enhanced with actual web search API
        # For now, return None to use database info only
        return None

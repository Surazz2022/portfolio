"""
Enhanced Response Generator
Generates varied, context-aware responses based on database info and web search
"""
from .models import PersonalInfo


def _pick(responses, user_message):
    """Deterministic selection — same question always returns the same variant."""
    return responses[hash(user_message.lower().strip()) % len(responses)]


def _not_in_portfolio(name, topic, user_message):
    """Standard honest response when a specific fact is not in the portfolio."""
    responses = [
        f"That specific information — {topic} — is not mentioned in {name}'s portfolio. I can only answer based on what is explicitly documented here. You may want to reach out to him directly for this.",
        f"I'm not certain about {topic}. It is not explicitly mentioned in {name}'s portfolio, and I'd rather be honest than guess. Feel free to contact him directly for accurate details.",
        f"I don't have information about {topic} in {name}'s portfolio. I only answer based on what is documented — I won't speculate on things not explicitly mentioned.",
    ]
    return _pick(responses, user_message)


class ResponseGenerator:
    """Generates strictly portfolio-grounded responses."""
    
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
                return _pick(responses, user_message)
        
        return _pick(responses, user_message)
    
    @staticmethod
    def generate_skills_response(personal_info, user_message, context=None):
        """Generate categorized skills response."""
        name = personal_info.full_name if personal_info else "Suraj Kharal"
        msg = user_message.lower()

        SKILL_CATEGORIES = {
            "AI / Agents":       ["langchain", "langgraph", "rag", "faiss", "semantic search",
                                   "sentence transformers", "groq", "llama", "ollama", "openai", "langsmith"],
            "NLP":               ["hugging face", "transformers", "text embeddings", "nlp", "ocr", "tesseract"],
            "Deep Learning":     ["tensorflow", "keras", "pytorch"],
            "ML":                ["scikit-learn", "arima", "lstm"],
            "Web / API":         ["fastapi", "django", "flask", "rest api"],
            "Data Analysis":     ["pandas", "numpy", "matplotlib", "seaborn", "plotly", "pydantic"],
            "Database":          ["postgresql", "mysql", "sql server", "qdrant", "azure blob"],
            "DevOps":            ["docker", "git", "github", "docker compose"],
            "Data Engineering":  ["etl", "data cleaning", "data integration", "sql", "ocr pipeline"],
        }

        # If asking about a specific skill, confirm and show its category
        for category, skills in SKILL_CATEGORIES.items():
            for skill in skills:
                if skill in msg:
                    return (
                        f"Yes, {name} has hands-on experience with {skill.title()}. "
                        f"It falls under his {category} skill set, alongside: "
                        f"{', '.join(s.title() for s in skills if s != skill)}."
                    )

        # General skills overview — formatted by category
        lines = [f"Here is a breakdown of {name}'s technical skills:\n"]
        for category, skills in SKILL_CATEGORIES.items():
            lines.append(f"• {category}: {', '.join(s.title() for s in skills)}")
        return "\n".join(lines)
    
    @staticmethod
    def generate_experience_response(personal_info, user_message, context=None):
        """Generate varied experience responses"""
        if not personal_info:
            return "Experience information is not available. Would you like to know about skills or contact information?"

        name = personal_info.full_name
        experience = personal_info.experience_summary
        title = personal_info.title
        msg = user_message.lower()

        salary_keywords = ['salary', 'compensation', 'pay', 'ctc', 'package', 'wage', 'stipend']
        if any(kw in msg for kw in salary_keywords):
            return _not_in_portfolio(name, "salary or compensation details", user_message)

        responses = [
            f"{name}'s experience: {experience}",
            f"Here's {name}'s professional background: {experience}",
            f"{name}, a {title}, has the following experience: {experience}",
            f"Professional experience: {experience}",
        ]

        return _pick(responses, user_message)
    
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
            response = _pick(responses, user_message)
            if linkedin:
                response += f"\n🔗 LinkedIn: {linkedin}"
            if github:
                response += f"\n💻 GitHub: {github}"
            return response
        
        return _pick(responses, user_message)
    
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
        
        return _pick(responses, user_message)
    
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
        
        return _pick(responses, user_message)
    
    @staticmethod
    def generate_research_response(personal_info, user_message, context=None):
        """Generate response about research interests"""
        name = personal_info.full_name if personal_info else "Suraj Kharal"
        msg = user_message.lower()

        # Specific facts not in the portfolio — answer honestly
        publication_keywords = [
            'publish', 'published', 'paper', 'papers', 'journal', 'conference',
            'arxiv', 'citation', 'cited', 'preprint', 'manuscript', 'article',
            'ieee', 'acm', 'springer', 'publication', 'peer review', 'peer-review'
        ]
        if any(kw in msg for kw in publication_keywords):
            return (
                f"{name} has one preprint on Zenodo (2026) investigating AI model robustness and failure behavior "
                f"in domain-specific, data-constrained real-world environments. "
                f"DOI: 10.5281/zenodo.20476820. It is a preprint, not a peer-reviewed journal paper."
            )

        conference_keywords = ['conference', 'workshop', 'symposium', 'seminar', 'talk', 'presentation', 'poster']
        if any(kw in msg for kw in conference_keywords):
            return _not_in_portfolio(name, "conference or workshop participation", user_message)

        grant_keywords = ['grant', 'funding', 'funded', 'scholarship', 'fellowship', 'award']
        if any(kw in msg for kw in grant_keywords):
            return _not_in_portfolio(name, "grants or research funding", user_message)

        responses = [
            f"{name}'s research interests:\n\n"
            f"• Large Language Models (LLMs)\n"
            f"• Multi-Agent AI & Chatbot Systems\n"
            f"• Natural Language Processing\n"
            f"• Toxicity Detection & Sentiment Analysis in Online Discourse\n"
            f"• Multimodal Vision AI & Image Classification\n\n"
            f"He also has a preprint on AI model robustness in domain-specific settings (Zenodo, 2026 — DOI: 10.5281/zenodo.20476820).",

            f"{name} is interested in: LLMs, Multi-Agent AI & Chatbot Systems, Natural Language Processing, Toxicity Detection & Sentiment Analysis, and Multimodal Vision AI & Image Classification. "
            f"He is actively looking for fully funded research opportunities in these areas.",

            f"{name}'s research spans LLMs, multi-agent AI systems, NLP, toxicity detection and sentiment analysis in online discourse, and multimodal vision AI. "
            f"He also has a preprint on AI model robustness in domain-specific, data-constrained environments. He is open to research collaborations and fully funded positions.",
        ]

        return _pick(responses, user_message)

    @staticmethod
    def generate_projects_response(personal_info, user_message, context=None):
        """Generate response about projects"""
        if not personal_info:
            name = "Suraj Kharal"
        else:
            name = personal_info.full_name

        responses = [
            f"{name} has built two key projects:\n\n"
            f"1. PubMed RAG Chatbot — An end-to-end RAG pipeline that parses 30,000+ biomedical papers, stores embeddings in FAISS, and uses Llama 3.3 70B via Groq for citation-grounded research answers. Exposed via FastAPI with 4 endpoints and containerized with Docker.\n\n"
            f"2. Sentiment Analysis App — Built on Instagram data from Kaggle, this project covers full EDA, text preprocessing, NLP and deep learning model training with hyperparameter tuning, evaluated on accuracy, precision, recall, and F1-score, and deployed with Flask and FastAPI.",

            f"Here are {name}'s notable projects:\n\n"
            f"• PubMed RAG Chatbot: RAG pipeline over 30k+ PubMed papers → FAISS vector index → Llama 3.3 70B (Groq) → FastAPI → Docker. Produces 31,520 searchable chunks with PMID citation traceability.\n\n"
            f"• Sentiment Analysis App: End-to-end NLP pipeline on Instagram data — EDA, tokenization, ML + deep learning models, hyperparameter tuning, Flask/FastAPI deployment.",

            f"{name}'s project work reflects his focus on production-ready AI systems. The PubMed RAG Chatbot demonstrates his ability to build scalable retrieval pipelines and integrate LLMs with real domain knowledge. The Sentiment Analysis App shows his foundation in classical NLP and deep learning workflows. Both projects are available on his GitHub.",
        ]

        return _pick(responses, user_message)

    @staticmethod
    def generate_education_response(personal_info, user_message, context=None):
        """Generate response about education, GPA, and certifications."""
        name = personal_info.full_name if personal_info else "Suraj Kharal"
        msg = user_message.lower()

        if any(kw in msg for kw in ['gpa', 'cgpa', 'grade', 'marks', 'percentage', 'score', 'result']):
            return (
                f"{name} completed his Bachelor of Information Management (BIM) from "
                f"Tribhuvan University, Oxford College, Butwal (2019–2023) with a GPA of 3.55."
            )

        if any(kw in msg for kw in ['certif', 'course', 'jovian', 'crewai', 'google developer']):
            return (
                f"{name} has completed the following courses:\n"
                f"• Crash Course — Jovian.ai\n"
                f"• Crash Course — Google Developers Group\n"
                f"• Crash Course — CrewAI"
            )

        return (
            f"{name}'s educational background:\n\n"
            f"🎓 Bachelor of Information Management (BIM)\n"
            f"   Tribhuvan University, Oxford College, Butwal\n"
            f"   2019 – 2023 | GPA: 3.55\n\n"
            f"📜 Certifications:\n"
            f"   • Crash Course — Jovian.ai\n"
            f"   • Crash Course — Google Developers Group\n"
            f"   • Crash Course — CrewAI\n\n"
            f"🏆 Extracurricular:\n"
            f"   • Secretary, IT Club — Oxford College\n"
            f"   • Participant — LECATHON 2022"
        )

    @staticmethod
    def generate_default_response(personal_info, user_message, context=None):
        """Return a scoped honest response when nothing matches."""
        name = personal_info.full_name if personal_info else "Suraj Kharal"
        msg = user_message.lower()

        # Catch common out-of-scope specific questions and be explicit
        age_keywords = ['age', 'how old', 'date of birth', 'dob', 'born']
        if any(kw in msg for kw in age_keywords):
            return _not_in_portfolio(name, "age or date of birth", user_message)

        gpa_keywords = ['gpa', 'grade', 'marks', 'percentage', 'score', 'cgpa']
        if any(kw in msg for kw in gpa_keywords):
            return (
                f"{name} completed a Bachelor of Information Management (BIM) from Tribhuvan University "
                f"(Oxford College, Butwal) with a GPA of 3.55. That is the only academic score mentioned in the portfolio."
            )

        language_keywords = ['language', 'speak', 'nepali', 'english', 'native language', 'mother tongue']
        if any(kw in msg for kw in language_keywords):
            return _not_in_portfolio(name, "spoken languages or language proficiency", user_message)

        return (
            f"I'm not sure I have information about that in {name}'s portfolio. "
            f"I can only answer based on what is explicitly documented here — I won't guess or speculate. "
            f"You can ask about his research interests, skills, projects, work experience, or contact details. "
            f"Or reach out to him directly for anything else."
        )
    
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
            'research': ResponseGenerator.generate_research_response,
            'projects': ResponseGenerator.generate_projects_response,
            'education': ResponseGenerator.generate_education_response,
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

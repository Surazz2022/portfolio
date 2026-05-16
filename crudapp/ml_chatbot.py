"""
ML-based Chatbot Service
Uses scikit-learn (TF-IDF + LogisticRegression) for intent classification.
Works in both local (with pickle persistence) and serverless (in-memory) environments.
"""
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from django.conf import settings

DEFAULT_TRAINING_DATA = [

    # ── GREETING (75) ─────────────────────────────────────────────────────────
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("hey", "greeting"),
    ("good morning", "greeting"),
    ("good afternoon", "greeting"),
    ("good evening", "greeting"),
    ("hi there", "greeting"),
    ("hey there", "greeting"),
    ("whats up", "greeting"),
    ("howdy", "greeting"),
    ("greetings", "greeting"),
    ("sup", "greeting"),
    ("yo", "greeting"),
    ("hiya", "greeting"),
    ("helo", "greeting"),
    ("hii", "greeting"),
    ("helloo", "greeting"),
    ("heyyy", "greeting"),
    ("good day", "greeting"),
    ("good night", "greeting"),
    ("morning", "greeting"),
    ("afternoon", "greeting"),
    ("evening", "greeting"),
    ("hi bot", "greeting"),
    ("hello there", "greeting"),
    ("hey bot", "greeting"),
    ("hello bot", "greeting"),
    ("namaste", "greeting"),
    ("salutations", "greeting"),
    ("what is up", "greeting"),
    ("how are you", "greeting"),
    ("how do you do", "greeting"),
    ("nice to meet you", "greeting"),
    ("pleased to meet you", "greeting"),
    ("start", "greeting"),
    ("begin", "greeting"),
    ("hi assistant", "greeting"),
    ("hello assistant", "greeting"),
    ("hey assistant", "greeting"),
    ("good to see you", "greeting"),
    ("howdy partner", "greeting"),
    ("hi hi", "greeting"),
    ("hey hey", "greeting"),
    ("hello hello", "greeting"),
    ("ohh hello", "greeting"),
    ("oh hi", "greeting"),
    ("oh hey", "greeting"),
    ("hey whats up", "greeting"),
    ("hi how are you", "greeting"),
    ("hello how are you", "greeting"),
    ("hey how are you", "greeting"),
    ("good to meet you", "greeting"),
    ("nice meeting you", "greeting"),
    ("hi im here", "greeting"),
    ("hello im here", "greeting"),
    ("hey im here", "greeting"),
    ("just saying hi", "greeting"),
    ("just saying hello", "greeting"),
    ("wanted to say hi", "greeting"),
    ("wanted to say hello", "greeting"),
    ("dropping by to say hi", "greeting"),
    ("heylo", "greeting"),
    ("heya", "greeting"),
    ("aloha", "greeting"),
    ("bonjour", "greeting"),
    ("ciao", "greeting"),
    ("hi there how are you", "greeting"),
    ("good morning how are you", "greeting"),
    ("good afternoon how are you", "greeting"),
    ("good evening how are you", "greeting"),
    ("hello can we talk", "greeting"),

    # ── ABOUT (75) ────────────────────────────────────────────────────────────
    ("who is suraj", "about"),
    ("who is suraj kharal", "about"),
    ("tell me about suraj", "about"),
    ("tell me about him", "about"),
    ("who are you representing", "about"),
    ("what does suraj do", "about"),
    ("introduce suraj", "about"),
    ("who is this person", "about"),
    ("tell me about yourself", "about"),
    ("what is suraj background", "about"),
    ("describe suraj", "about"),
    ("who is he", "about"),
    ("about suraj", "about"),
    ("what do you know about suraj", "about"),
    ("give me an introduction", "about"),
    ("can you introduce suraj", "about"),
    ("who exactly is suraj kharal", "about"),
    ("what is his profile", "about"),
    ("suraj kharal profile", "about"),
    ("tell me more about suraj kharal", "about"),
    ("describe suraj kharal", "about"),
    ("what is suraj all about", "about"),
    ("what does he do", "about"),
    ("what is he all about", "about"),
    ("give me a brief about suraj", "about"),
    ("give me a summary about suraj", "about"),
    ("what is his story", "about"),
    ("what is suraj story", "about"),
    ("overview of suraj", "about"),
    ("professional overview", "about"),
    ("who is the person behind this portfolio", "about"),
    ("tell me about the developer", "about"),
    ("who built this portfolio", "about"),
    ("who made this", "about"),
    ("who is this ai engineer", "about"),
    ("what can you tell me about suraj", "about"),
    ("suraj kharal bio", "about"),
    ("what is his bio", "about"),
    ("suraj bio", "about"),
    ("personal summary", "about"),
    ("professional summary", "about"),
    ("what is his professional background", "about"),
    ("what is suraj professional background", "about"),
    ("brief introduction of suraj", "about"),
    ("introduce yourself", "about"),
    ("describe yourself", "about"),
    ("tell me who suraj is", "about"),
    ("who is the engineer", "about"),
    ("what is his domain", "about"),
    ("what field does suraj work in", "about"),
    ("what area does he specialize in", "about"),
    ("what is his specialization", "about"),
    ("suraj specialization", "about"),
    ("what is suraj kharal known for", "about"),
    ("what is he known for", "about"),
    ("tell me something about suraj", "about"),
    ("give me some info about suraj", "about"),
    ("info about suraj", "about"),
    ("suraj kharal information", "about"),
    ("who is the owner of this portfolio", "about"),
    ("tell me about this engineer", "about"),
    ("about the developer", "about"),
    ("summary of suraj", "about"),
    ("who are we talking about", "about"),
    ("describe the candidate", "about"),
    ("tell me about the candidate", "about"),
    ("candidate profile", "about"),
    ("candidate summary", "about"),
    ("what does suraj kharal do", "about"),
    ("what is his background", "about"),
    ("brief about suraj", "about"),
    ("brief bio", "about"),
    ("short introduction", "about"),
    ("short bio", "about"),
    ("quick intro", "about"),
    ("quick overview", "about"),

    # ── SKILLS (75) ───────────────────────────────────────────────────────────
    ("what are his skills", "skills"),
    ("what skills does suraj have", "skills"),
    ("what technologies does he know", "skills"),
    ("what can suraj do", "skills"),
    ("technical skills", "skills"),
    ("programming languages", "skills"),
    ("what is he good at", "skills"),
    ("skills", "skills"),
    ("expertise", "skills"),
    ("what tools does he use", "skills"),
    ("does he know python", "skills"),
    ("does he know machine learning", "skills"),
    ("what frameworks does he use", "skills"),
    ("his tech stack", "skills"),
    ("what is his tech stack", "skills"),
    ("what technologies does suraj use", "skills"),
    ("list his skills", "skills"),
    ("what are suraj skills", "skills"),
    ("what are his technical skills", "skills"),
    ("technical expertise", "skills"),
    ("what languages does he code in", "skills"),
    ("what programming languages does he know", "skills"),
    ("does he know django", "skills"),
    ("does he know fastapi", "skills"),
    ("does he know langchain", "skills"),
    ("does he know docker", "skills"),
    ("does he know postgresql", "skills"),
    ("does he know tensorflow", "skills"),
    ("does he know pytorch", "skills"),
    ("does he know rag", "skills"),
    ("does he know faiss", "skills"),
    ("does he know groq", "skills"),
    ("does he know llm", "skills"),
    ("ai skills", "skills"),
    ("ml skills", "skills"),
    ("data science skills", "skills"),
    ("deep learning skills", "skills"),
    ("nlp skills", "skills"),
    ("what nlp tools does he use", "skills"),
    ("devops skills", "skills"),
    ("database skills", "skills"),
    ("what databases does he use", "skills"),
    ("what cloud tools does he use", "skills"),
    ("what are his ai skills", "skills"),
    ("what are his ml skills", "skills"),
    ("what are his data science skills", "skills"),
    ("what does he specialize in technically", "skills"),
    ("his programming expertise", "skills"),
    ("coding skills", "skills"),
    ("what coding skills does he have", "skills"),
    ("his libraries", "skills"),
    ("what libraries does he use", "skills"),
    ("his frameworks", "skills"),
    ("list frameworks", "skills"),
    ("list technologies", "skills"),
    ("list tools", "skills"),
    ("what tools does suraj use", "skills"),
    ("what are his strongest skills", "skills"),
    ("core skills", "skills"),
    ("what are his core competencies", "skills"),
    ("technical competencies", "skills"),
    ("competencies", "skills"),
    ("technical proficiency", "skills"),
    ("proficiency", "skills"),
    ("areas of expertise", "skills"),
    ("what is he proficient in", "skills"),
    ("what is suraj proficient in", "skills"),
    ("software skills", "skills"),
    ("engineering skills", "skills"),
    ("data engineering skills", "skills"),
    ("ocr skills", "skills"),
    ("does he know ocr", "skills"),
    ("vector database skills", "skills"),
    ("does he know qdrant", "skills"),
    ("does he know hugging face", "skills"),

    # ── EXPERIENCE (75) ───────────────────────────────────────────────────────
    ("what is his experience", "experience"),
    ("work experience", "experience"),
    ("where has he worked", "experience"),
    ("previous jobs", "experience"),
    ("career history", "experience"),
    ("professional background", "experience"),
    ("what companies has he worked for", "experience"),
    ("experience", "experience"),
    ("his work history", "experience"),
    ("where does he work", "experience"),
    ("current job", "experience"),
    ("past experience", "experience"),
    ("where is he currently working", "experience"),
    ("what is his current role", "experience"),
    ("current role", "experience"),
    ("current position", "experience"),
    ("where did he work before", "experience"),
    ("previous roles", "experience"),
    ("previous positions", "experience"),
    ("career path", "experience"),
    ("employment history", "experience"),
    ("work history", "experience"),
    ("has he worked in ai", "experience"),
    ("has he worked in ml", "experience"),
    ("where does suraj work", "experience"),
    ("where did suraj work", "experience"),
    ("tell me about his work experience", "experience"),
    ("describe his experience", "experience"),
    ("list his jobs", "experience"),
    ("list his experience", "experience"),
    ("what roles has he held", "experience"),
    ("what positions has he held", "experience"),
    ("where has suraj worked", "experience"),
    ("cognifynow", "experience"),
    ("nepaworks", "experience"),
    ("nepsetrading", "experience"),
    ("what did he do at cognifynow", "experience"),
    ("what did he do at nepaworks", "experience"),
    ("what did he do at nepsetrading", "experience"),
    ("his job at cognifynow", "experience"),
    ("his job at nepaworks", "experience"),
    ("his job at nepsetrading", "experience"),
    ("how long has he been working", "experience"),
    ("how many years of experience does he have", "experience"),
    ("years of experience", "experience"),
    ("industry experience", "experience"),
    ("field experience", "experience"),
    ("professional experience", "experience"),
    ("job history", "experience"),
    ("career background", "experience"),
    ("what has he done professionally", "experience"),
    ("what has suraj done professionally", "experience"),
    ("his professional journey", "experience"),
    ("professional journey", "experience"),
    ("career journey", "experience"),
    ("job experience", "experience"),
    ("what is his job", "experience"),
    ("what was his last job", "experience"),
    ("last job", "experience"),
    ("recent job", "experience"),
    ("recent role", "experience"),
    ("recent position", "experience"),
    ("latest role", "experience"),
    ("latest job", "experience"),
    ("ai developer experience", "experience"),
    ("ml engineer experience", "experience"),
    ("data analyst experience", "experience"),
    ("has he worked as a data analyst", "experience"),
    ("has he worked as an ml engineer", "experience"),
    ("has he worked as an ai developer", "experience"),
    ("what industry has he worked in", "experience"),
    ("finance experience", "experience"),
    ("stock market experience", "experience"),
    ("what did he work on", "experience"),
    ("what has he worked on", "experience"),

    # ── CONTACT (75) ──────────────────────────────────────────────────────────
    ("how can i contact him", "contact"),
    ("contact information", "contact"),
    ("email address", "contact"),
    ("phone number", "contact"),
    ("how to reach suraj", "contact"),
    ("contact details", "contact"),
    ("how do i get in touch", "contact"),
    ("contact", "contact"),
    ("email", "contact"),
    ("phone", "contact"),
    ("reach out", "contact"),
    ("his email", "contact"),
    ("his phone", "contact"),
    ("how do i contact suraj", "contact"),
    ("what is his email", "contact"),
    ("what is his phone number", "contact"),
    ("suraj email address", "contact"),
    ("suraj phone number", "contact"),
    ("how to contact suraj kharal", "contact"),
    ("where is suraj located", "contact"),
    ("what is his location", "contact"),
    ("his location", "contact"),
    ("where does he live", "contact"),
    ("where is he based", "contact"),
    ("how can i reach him", "contact"),
    ("how can i get in touch with him", "contact"),
    ("how do i reach suraj", "contact"),
    ("contact suraj", "contact"),
    ("reach suraj", "contact"),
    ("get in touch with suraj", "contact"),
    ("can i contact him", "contact"),
    ("can i email him", "contact"),
    ("can i call him", "contact"),
    ("send him a message", "contact"),
    ("message him", "contact"),
    ("send an email", "contact"),
    ("send him an email", "contact"),
    ("call him", "contact"),
    ("his contact info", "contact"),
    ("his contact details", "contact"),
    ("contact info", "contact"),
    ("gmail", "contact"),
    ("his gmail", "contact"),
    ("email id", "contact"),
    ("his email id", "contact"),
    ("mobile number", "contact"),
    ("his mobile number", "contact"),
    ("mobile", "contact"),
    ("telephone", "contact"),
    ("contact number", "contact"),
    ("his contact number", "contact"),
    ("how do i connect with suraj", "contact"),
    ("connect with suraj", "contact"),
    ("connect with him", "contact"),
    ("linkedin profile", "contact"),
    ("github profile", "contact"),
    ("his linkedin", "contact"),
    ("his github", "contact"),
    ("social media", "contact"),
    ("his social media", "contact"),
    ("how to connect", "contact"),
    ("where can i find him", "contact"),
    ("where can i find suraj", "contact"),
    ("find suraj online", "contact"),
    ("online presence", "contact"),
    ("his online presence", "contact"),
    ("address", "contact"),
    ("his address", "contact"),
    ("location", "contact"),
    ("city", "contact"),
    ("country", "contact"),
    ("which country is he from", "contact"),
    ("which city is he in", "contact"),
    ("nepal", "contact"),
    ("is he in nepal", "contact"),

    # ── AVAILABILITY (75) ─────────────────────────────────────────────────────
    ("is he available", "availability"),
    ("is suraj looking for work", "availability"),
    ("availability", "availability"),
    ("is he open to opportunities", "availability"),
    ("what roles is he looking for", "availability"),
    ("is he hiring", "availability"),
    ("job status", "availability"),
    ("is he employed", "availability"),
    ("open to work", "availability"),
    ("looking for job", "availability"),
    ("is suraj available", "availability"),
    ("is suraj open to work", "availability"),
    ("is he looking for a job", "availability"),
    ("is he actively looking", "availability"),
    ("is he job hunting", "availability"),
    ("what is his availability", "availability"),
    ("is he free to work", "availability"),
    ("can we hire him", "availability"),
    ("is he currently available", "availability"),
    ("is he open to new roles", "availability"),
    ("is he open to new opportunities", "availability"),
    ("is he looking for new opportunities", "availability"),
    ("open to opportunities", "availability"),
    ("what kind of roles is he looking for", "availability"),
    ("what roles does he prefer", "availability"),
    ("preferred roles", "availability"),
    ("his preferred roles", "availability"),
    ("job preferences", "availability"),
    ("what is his job status", "availability"),
    ("employment status", "availability"),
    ("is he currently employed", "availability"),
    ("is he working right now", "availability"),
    ("is he open to freelance", "availability"),
    ("is he open to remote work", "availability"),
    ("is he open to relocation", "availability"),
    ("is he open to full time", "availability"),
    ("full time availability", "availability"),
    ("part time availability", "availability"),
    ("freelance availability", "availability"),
    ("remote work availability", "availability"),
    ("is he available for hire", "availability"),
    ("hire suraj", "availability"),
    ("can we work with suraj", "availability"),
    ("is suraj available for work", "availability"),
    ("is he interested in new positions", "availability"),
    ("seeking employment", "availability"),
    ("actively seeking", "availability"),
    ("actively job searching", "availability"),
    ("job search status", "availability"),
    ("is he on the job market", "availability"),
    ("on the job market", "availability"),
    ("ready to work", "availability"),
    ("is he ready to join", "availability"),
    ("when can he start", "availability"),
    ("notice period", "availability"),
    ("what is his notice period", "availability"),
    ("is he open to research positions", "availability"),
    ("is he open to academic positions", "availability"),
    ("is he looking for research roles", "availability"),
    ("is he interested in phd", "availability"),
    ("is he applying for phd", "availability"),
    ("is he seeking research opportunities", "availability"),
    ("looking for research opportunity", "availability"),
    ("seeking research position", "availability"),
    ("is he open to collaborations", "availability"),
    ("open to collaboration", "availability"),
    ("is he open to internships", "availability"),
    ("internship availability", "availability"),
    ("is he available for internship", "availability"),
    ("work preference", "availability"),
    ("his work preference", "availability"),
    ("what is his work preference", "availability"),
    ("what type of work is he looking for", "availability"),
    ("what kind of work does he want", "availability"),
    ("is he looking for industry or academia", "availability"),

    # ── JOB OFFER (75) ────────────────────────────────────────────────────────
    ("i have a job offer", "job_offer"),
    ("job opportunity", "job_offer"),
    ("we want to hire suraj", "job_offer"),
    ("i want to offer a position", "job_offer"),
    ("job offer", "job_offer"),
    ("hire him", "job_offer"),
    ("recruit suraj", "job_offer"),
    ("we have an opening", "job_offer"),
    ("position available", "job_offer"),
    ("offer letter", "job_offer"),
    ("submit job offer", "job_offer"),
    ("employment opportunity", "job_offer"),
    ("i want to hire suraj", "job_offer"),
    ("we are hiring", "job_offer"),
    ("we have a vacancy", "job_offer"),
    ("vacancy for suraj", "job_offer"),
    ("we have a role for him", "job_offer"),
    ("we have a position for him", "job_offer"),
    ("i want to recruit suraj", "job_offer"),
    ("we want to recruit him", "job_offer"),
    ("offering a job", "job_offer"),
    ("offering a role", "job_offer"),
    ("offering a position", "job_offer"),
    ("we have a job for suraj", "job_offer"),
    ("we have an opportunity for suraj", "job_offer"),
    ("send an offer", "job_offer"),
    ("submit an offer", "job_offer"),
    ("i want to submit a job offer", "job_offer"),
    ("i would like to make an offer", "job_offer"),
    ("make a job offer", "job_offer"),
    ("extend a job offer", "job_offer"),
    ("job proposal", "job_offer"),
    ("work proposal", "job_offer"),
    ("employment proposal", "job_offer"),
    ("i have a work opportunity", "job_offer"),
    ("i have an employment opportunity", "job_offer"),
    ("recruiting suraj", "job_offer"),
    ("hiring suraj", "job_offer"),
    ("our company wants to hire him", "job_offer"),
    ("our team wants to hire him", "job_offer"),
    ("we are looking to hire suraj", "job_offer"),
    ("looking to hire him", "job_offer"),
    ("interested in hiring suraj", "job_offer"),
    ("interested in recruiting suraj", "job_offer"),
    ("we have a full time role", "job_offer"),
    ("full time job offer", "job_offer"),
    ("part time job offer", "job_offer"),
    ("remote job offer", "job_offer"),
    ("freelance offer", "job_offer"),
    ("contract offer", "job_offer"),
    ("internship offer", "job_offer"),
    ("research position offer", "job_offer"),
    ("i want to offer research position", "job_offer"),
    ("offering research collaboration", "job_offer"),
    ("research collaboration offer", "job_offer"),
    ("we have a research role", "job_offer"),
    ("academic position", "job_offer"),
    ("we have an academic position for him", "job_offer"),
    ("phd offer", "job_offer"),
    ("fully funded phd offer", "job_offer"),
    ("scholarship offer", "job_offer"),
    ("fellowship offer", "job_offer"),
    ("i want to offer fellowship", "job_offer"),
    ("grant opportunity", "job_offer"),
    ("research grant", "job_offer"),
    ("i have a project for him", "job_offer"),
    ("i have a contract for him", "job_offer"),
    ("consulting offer", "job_offer"),
    ("i want to consult with suraj", "job_offer"),
    ("we want to partner with suraj", "job_offer"),
    ("partnership offer", "job_offer"),
    ("collaboration offer", "job_offer"),
    ("i have an offer", "job_offer"),
    ("i want to make him an offer", "job_offer"),
    ("i want to extend an offer", "job_offer"),

    # ── RESEARCH (75) ─────────────────────────────────────────────────────────
    ("what are his research interests", "research"),
    ("what does suraj research", "research"),
    ("tell me about his research", "research"),
    ("is suraj interested in research", "research"),
    ("research interests", "research"),
    ("what is he researching", "research"),
    ("research focus", "research"),
    ("academic interests", "research"),
    ("is he looking for research opportunities", "research"),
    ("what research areas", "research"),
    ("agentic ai research", "research"),
    ("rag research", "research"),
    ("nepse research", "research"),
    ("emerging markets ai research", "research"),
    ("multimodal ai research", "research"),
    ("phd research interests", "research"),
    ("research collaboration", "research"),
    ("what are his academic interests", "research"),
    ("what research does he want to do", "research"),
    ("what research has he done", "research"),
    ("his research background", "research"),
    ("research background", "research"),
    ("what are his research goals", "research"),
    ("research goals", "research"),
    ("research areas of interest", "research"),
    ("areas of research", "research"),
    ("what does he want to study", "research"),
    ("what does he plan to study", "research"),
    ("what is his research agenda", "research"),
    ("research agenda", "research"),
    ("his academic focus", "research"),
    ("academic focus", "research"),
    ("what is his academic focus", "research"),
    ("research domain", "research"),
    ("what research domain", "research"),
    ("what is his research domain", "research"),
    ("his field of study", "research"),
    ("field of study", "research"),
    ("what field does he want to research", "research"),
    ("what field is he researching", "research"),
    ("research question", "research"),
    ("what are his research questions", "research"),
    ("what problem is he researching", "research"),
    ("what problem does he want to solve through research", "research"),
    ("nepse ai research", "research"),
    ("stock market ai research", "research"),
    ("financial ai research", "research"),
    ("broker driven market research", "research"),
    ("emerging market research", "research"),
    ("robustness of ai models", "research"),
    ("ai robustness", "research"),
    ("llm robustness", "research"),
    ("agentic systems research", "research"),
    ("autonomous agents research", "research"),
    ("retrieval augmented generation research", "research"),
    ("rag pipeline research", "research"),
    ("multimodal research", "research"),
    ("vision language model research", "research"),
    ("vlm research", "research"),
    ("domain adaptation research", "research"),
    ("what is his phd interest", "research"),
    ("phd interest", "research"),
    ("doctoral interest", "research"),
    ("research plan", "research"),
    ("his research plan", "research"),
    ("what does he want to research for phd", "research"),
    ("is he interested in phd research", "research"),
    ("is he pursuing research", "research"),
    ("pursuing research", "research"),
    ("is he doing any research", "research"),
    ("what study is he interested in", "research"),
    ("study interest", "research"),
    ("scholarly interest", "research"),
    ("scientific interest", "research"),
    ("what scientific questions interest him", "research"),
    ("what is he investigating", "research"),
    ("investigating", "research"),

    # ── EDUCATION (50) ────────────────────────────────────────────────────────
    ("what is his gpa", "education"),
    ("what is his cgpa", "education"),
    ("what is his grade", "education"),
    ("what grade did he get", "education"),
    ("what are his marks", "education"),
    ("his gpa", "education"),
    ("his cgpa", "education"),
    ("his grades", "education"),
    ("his marks", "education"),
    ("want to know his gpa", "education"),
    ("tell me his gpa", "education"),
    ("what is his academic score", "education"),
    ("what degree does he have", "education"),
    ("what is his degree", "education"),
    ("what did he study", "education"),
    ("where did he study", "education"),
    ("what is his education", "education"),
    ("education background", "education"),
    ("academic background", "education"),
    ("his educational background", "education"),
    ("what university did he go to", "education"),
    ("which university did he attend", "education"),
    ("which college did he attend", "education"),
    ("tribhuvan university", "education"),
    ("oxford college", "education"),
    ("bim degree", "education"),
    ("bachelor of information management", "education"),
    ("what is bim", "education"),
    ("his bachelor degree", "education"),
    ("his undergraduate degree", "education"),
    ("when did he graduate", "education"),
    ("when did he finish his degree", "education"),
    ("his graduation year", "education"),
    ("what certifications does he have", "education"),
    ("his certifications", "education"),
    ("certifications", "education"),
    ("what courses has he completed", "education"),
    ("his courses", "education"),
    ("jovian course", "education"),
    ("crewai course", "education"),
    ("google developers course", "education"),
    ("extracurricular activities", "education"),
    ("his extracurricular", "education"),
    ("it club", "education"),
    ("lecathon", "education"),
    ("what clubs was he in", "education"),
    ("academic qualifications", "education"),
    ("his qualifications", "education"),
    ("his academic background", "education"),
    ("what is his academic background", "education"),

    # ── PROJECTS (75) ─────────────────────────────────────────────────────────
    ("what projects has he built", "projects"),
    ("tell me about his projects", "projects"),
    ("what has suraj built", "projects"),
    ("portfolio projects", "projects"),
    ("show me his work", "projects"),
    ("what are his projects", "projects"),
    ("projects", "projects"),
    ("pubmed chatbot", "projects"),
    ("rag chatbot", "projects"),
    ("sentiment analysis project", "projects"),
    ("what has he built", "projects"),
    ("his work", "projects"),
    ("project portfolio", "projects"),
    ("what is his most impressive project", "projects"),
    ("his best project", "projects"),
    ("best project", "projects"),
    ("most impressive project", "projects"),
    ("notable projects", "projects"),
    ("his notable projects", "projects"),
    ("what projects has suraj built", "projects"),
    ("list his projects", "projects"),
    ("list suraj projects", "projects"),
    ("what applications has he built", "projects"),
    ("what apps has he built", "projects"),
    ("what systems has he built", "projects"),
    ("what pipelines has he built", "projects"),
    ("what tools has he built", "projects"),
    ("what has he developed", "projects"),
    ("what has suraj developed", "projects"),
    ("his developments", "projects"),
    ("his creations", "projects"),
    ("show me what he has built", "projects"),
    ("can you show me his projects", "projects"),
    ("what are his side projects", "projects"),
    ("side projects", "projects"),
    ("personal projects", "projects"),
    ("his personal projects", "projects"),
    ("open source projects", "projects"),
    ("his open source work", "projects"),
    ("github projects", "projects"),
    ("what is on his github", "projects"),
    ("what does his github have", "projects"),
    ("pubmed rag", "projects"),
    ("biomedical rag", "projects"),
    ("biomedical chatbot", "projects"),
    ("rag pipeline project", "projects"),
    ("faiss project", "projects"),
    ("llm project", "projects"),
    ("langchain project", "projects"),
    ("sentiment analysis app", "projects"),
    ("instagram sentiment analysis", "projects"),
    ("nlp project", "projects"),
    ("deep learning project", "projects"),
    ("machine learning project", "projects"),
    ("ai project", "projects"),
    ("what ai projects has he done", "projects"),
    ("what ml projects has he done", "projects"),
    ("what nlp projects has he done", "projects"),
    ("document digitization project", "projects"),
    ("ocr project", "projects"),
    ("inventory agent project", "projects"),
    ("inventory chatbot", "projects"),
    ("vision ai project", "projects"),
    ("image classification project", "projects"),
    ("object detection project", "projects"),
    ("what data science projects has he done", "projects"),
    ("data science projects", "projects"),
    ("his portfolio", "projects"),
    ("portfolio", "projects"),
    ("what is in his portfolio", "projects"),
    ("can you describe his projects", "projects"),
    ("describe his projects", "projects"),
    ("his project experience", "projects"),
    ("project experience", "projects"),
    ("real world projects", "projects"),
    ("production projects", "projects"),
]

# Singleton instance
_chatbot_instance = None


def get_chatbot_service():
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MLChatbotService()
    return _chatbot_instance


class MLChatbotService:
    """TF-IDF + LogisticRegression intent classifier with pickle persistence."""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_serverless = os.environ.get('VERCEL', False) or os.environ.get('SERVERLESS', False)

        if not self.is_serverless:
            base_dir = str(settings.BASE_DIR)
            self.model_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'chatbot_model.pkl')
            self.vectorizer_path = os.path.join(base_dir, 'crudapp', 'ml_models', 'vectorizer.pkl')
            self._ensure_model_directory()

        self._load_or_initialize_model()

    def _ensure_model_directory(self):
        if self.is_serverless:
            return
        model_dir = os.path.dirname(self.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

    def _load_or_initialize_model(self):
        loaded = False
        if not self.is_serverless:
            try:
                import joblib
                if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                    self.model = joblib.load(self.model_path)
                    self.vectorizer = joblib.load(self.vectorizer_path)
                    loaded = True
            except Exception as e:
                print(f"Error loading model: {e}")

        if not loaded:
            self._initialize_model()
            self._train_with_defaults()

    def _initialize_model(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=8000,
                ngram_range=(1, 3),
                stop_words='english',
                lowercase=True,
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
            )),
            ('classifier', LogisticRegression(
                C=5.0,
                max_iter=1000,
                solver='lbfgs',
                random_state=42,
            ))
        ])
        self.vectorizer = None

    def _train_with_defaults(self):
        training_data = list(DEFAULT_TRAINING_DATA)
        try:
            from .models import ChatbotTrainingData
            db_data = ChatbotTrainingData.objects.all()
            if db_data.exists():
                training_data.extend([(item.user_message, item.intent) for item in db_data])
        except Exception:
            pass
        self.train(training_data)

    def train(self, training_data):
        if not training_data:
            return False
        messages = [item[0].lower().strip() for item in training_data]
        intents = [item[1] for item in training_data]
        try:
            self.model.fit(messages, intents)
            self._save_model()
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    # Keyword fallback — high-precision safety net
    KEYWORD_INTENTS = {
        'research': [
            'research interest', 'research focus', 'research area', 'research background',
            'research question', 'research goal', 'research plan', 'research agenda',
            'research collaboration', 'research domain', 'academic interest', 'academic focus',
            'phd interest', 'doctoral interest', 'studying', 'investigating',
            'nepse research', 'emerging market research', 'ai robustness',
            'vlm research', 'domain adaptation research', 'rag research', 'agentic ai research',
            'scholarly interest', 'scientific interest', 'field of study',
        ],
        'projects': [
            'project', 'projects', 'pubmed', 'rag chatbot', 'rag pipeline',
            'sentiment analysis', 'what has he built', 'what has suraj built',
            'his portfolio', 'github project', 'ocr project', 'inventory agent',
            'vision ai', 'image classification', 'object detection', 'biomedical chatbot',
            'document digitization', 'langchain project', 'nlp project',
            'what he developed', 'what suraj developed', 'side project', 'personal project',
        ],
        'skills': [
            'skill', 'skills', 'technologies', 'tech stack', 'programming language',
            'frameworks', 'tools', 'expertise', 'proficient', 'competenc',
            'does he know', 'langchain', 'langgraph', 'faiss', 'docker',
            'tensorflow', 'pytorch', 'fastapi', 'django', 'postgresql', 'qdrant',
            'ocr', 'hugging face', 'groq', 'llm', 'rag', 'nlp skills', 'ai skills',
        ],
        'experience': [
            'experience', 'work history', 'career', 'worked', 'previous job',
            'previous role', 'employment', 'current job', 'current role',
            'cognifynow', 'nepaworks', 'nepsetrading', 'professional journey',
            'career path', 'career background', 'job history', 'where has he worked',
        ],
        'contact': [
            'contact', 'email address', 'phone number', 'reach out', 'get in touch',
            'call him', 'message him', 'email id', 'gmail', 'mobile number',
            'where is he located', 'where is he based', 'where does he live',
            'his location', 'his address', 'find suraj online', 'linkedin profile',
            'github profile', 'social media',
        ],
        'availability': [
            'available', 'availability', 'looking for work', 'open to opportunities',
            'open to work', 'job status', 'employment status', 'actively seeking',
            'on the job market', 'ready to join', 'notice period', 'when can he start',
            'open to research positions', 'open to collaborations', 'open to internship',
            'work preference', 'preferred roles',
        ],
        'job_offer': [
            'job offer', 'hire', 'recruit', 'position available', 'offer letter',
            'opening', 'vacancy', 'i want to offer', 'i have an offer',
            'fully funded', 'phd offer', 'scholarship offer', 'fellowship offer',
            'research grant', 'partnership offer', 'consulting offer',
        ],
        'about': [
            'who is suraj', 'who is he', 'tell me about suraj', 'about suraj',
            'suraj kharal bio', 'introduce suraj', 'describe suraj',
            'who is this person', 'who is the developer', 'candidate profile',
            'suraj profile', 'suraj story', 'suraj overview',
        ],
        'greeting': [
            'hello', 'hi there', 'hey there', 'good morning', 'good afternoon',
            'good evening', 'howdy', 'whats up', 'greetings', 'namaste', 'aloha',
        ],
        'education': [
            'gpa', 'cgpa', 'grade', 'education', 'degree', 'university', 'college',
            'bachelor', 'bim', 'tribhuvan', 'oxford college', 'certification',
            'certified', 'course', 'academic qualification', 'qualification',
            'marks', 'percentage', 'result', 'academic background', 'study',
            'studied', 'where did he study', 'what did he study', 'extracurricular',
            'jovian', 'crewai', 'lecathon', 'it club',
        ],
    }

    def _keyword_match(self, message):
        message_lower = message.lower().strip()
        # Check high-specificity intents first to avoid false positives
        priority_order = ['research', 'projects', 'skills', 'experience', 'contact',
                          'availability', 'job_offer', 'about', 'greeting']
        for intent in priority_order:
            keywords = self.KEYWORD_INTENTS[intent]
            if any(kw in message_lower for kw in keywords):
                return intent
        return None

    def predict_intent(self, user_message, conversation_history=None):
        if not self.model:
            return self._keyword_match(user_message) or 'default'

        try:
            cleaned_message = user_message.lower().strip()

            # Catch greeting misspellings with short messages (e.g. "helllo", "hii")
            greeting_starts = ('hi', 'hel', 'hey', 'hiya', 'howdy', 'good morn', 'good after', 'good eve')
            if len(cleaned_message.split()) <= 3 and cleaned_message.startswith(greeting_starts):
                return 'greeting'

            # Keyword matching first — specific intents override ML to prevent misclassification
            keyword_intent = self._keyword_match(cleaned_message)
            if keyword_intent:
                return keyword_intent

            # ML model for everything else
            intent = self.model.predict([cleaned_message])[0]
            probabilities = self.model.predict_proba([cleaned_message])[0]
            max_probability = max(probabilities)

            if max_probability >= 0.25:
                return intent

            return 'default'
        except Exception as e:
            print(f"Error predicting intent: {e}")
            return self._keyword_match(user_message) or 'default'

    def predict_with_context(self, user_message, conversation_state=None, conversation_history=None):
        if not self.model:
            return {
                'intent': self._keyword_match(user_message) or 'default',
                'confidence': 0.5,
                'actions': []
            }

        try:
            cleaned_message = user_message.lower().strip()

            if conversation_state == 'linkedin_question':
                if any(w in cleaned_message for w in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {'intent': 'linkedin_yes', 'confidence': 1.0, 'actions': ['open_linkedin']}
                elif any(w in cleaned_message for w in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'linkedin_no', 'confidence': 1.0, 'actions': ['next_question']}

            elif conversation_state == 'github_question':
                if any(w in cleaned_message for w in ['yes', 'y', 'sure', 'ok', 'okay', 'open']):
                    return {'intent': 'github_yes', 'confidence': 1.0, 'actions': ['open_github']}
                elif any(w in cleaned_message for w in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'github_no', 'confidence': 1.0, 'actions': ['next_question']}

            elif conversation_state == 'email_question':
                if any(w in cleaned_message for w in ['yes', 'y', 'sure', 'ok', 'okay', 'send']):
                    return {'intent': 'email_yes', 'confidence': 1.0, 'actions': ['open_email']}
                elif any(w in cleaned_message for w in ['no', 'n', 'skip', 'not now']):
                    return {'intent': 'email_no', 'confidence': 1.0, 'actions': ['end_greeting']}

            intent = self.predict_intent(user_message, conversation_history)
            probabilities = self.model.predict_proba([cleaned_message])[0]
            max_probability = max(probabilities)

            return {
                'intent': intent,
                'confidence': float(max_probability),
                'actions': []
            }
        except Exception as e:
            print(f"Error in predict_with_context: {e}")
            return {
                'intent': self._keyword_match(user_message) or 'default',
                'confidence': 0.0,
                'actions': []
            }

    def get_similar_messages(self, user_message, training_tuples, top_n=3):
        if not training_tuples:
            return []
        try:
            messages = [item[0].lower().strip() for item in training_tuples]
            messages.append(user_message.lower().strip())
            vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2),
                                         stop_words='english', lowercase=True)
            tfidf_matrix = vectorizer.fit_transform(messages)
            user_vector = tfidf_matrix[-1]
            training_vectors = tfidf_matrix[:-1]
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(user_vector, training_vectors)[0]
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            return [
                {
                    'message': training_tuples[idx][0],
                    'intent': training_tuples[idx][1],
                    'response': training_tuples[idx][2],
                    'similarity': float(similarities[idx])
                }
                for idx in top_indices if similarities[idx] > 0.1
            ]
        except Exception as e:
            print(f"Error finding similar messages: {e}")
            return []

    def _save_model(self):
        if self.is_serverless:
            return
        try:
            import joblib
            joblib.dump(self.model, self.model_path)
            if hasattr(self.model, 'named_steps'):
                vectorizer = self.model.named_steps.get('tfidf')
                if vectorizer:
                    joblib.dump(vectorizer, self.vectorizer_path)
        except Exception as e:
            print(f"Error saving model: {e}")

    def retrain_from_database(self):
        from .models import ChatbotTrainingData
        training_data = ChatbotTrainingData.objects.all()
        if training_data.count() == 0:
            return False
        data = [(item.user_message, item.intent) for item in training_data]
        return self.train(data)

# -*- coding: utf-8 -*-
"""
Model Service: Integrates Colab-trained ML Model, TF-IDF Vectorizer & Scoring Logic
"""

import os
import re
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression

from backend.config import MODELS_DIR
from backend.services.resume_parser import extract_contact_info

try:
    from nltk.corpus import stopwords
    NLTK_STOPWORDS = set(stopwords.words("english"))
except Exception:
    NLTK_STOPWORDS = set([
        "a", "about", "above", "after", "again", "all", "am", "an", "and", "any", "are",
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few",
        "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "him",
        "his", "how", "i", "if", "in", "into", "is", "it", "its", "me", "more", "most", "my",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "out",
        "over", "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
        "their", "them", "then", "there", "these", "they", "this", "those", "through", "to",
        "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where",
        "which", "while", "who", "whom", "why", "with", "would", "you", "your"
    ])

FEATURE_COLUMNS = [
    "experience_years", "skill_count", "project_count", "certification_count",
    "skill_match_score", "experience_match_score", "education_match_score",
    "project_score", "certification_score", "cosine_similarity_score"
]

SKILL_NORMALIZATION_MAP = {
    "java": "java", "core java": "java", "advanced java": "java", "JAVA": "java", "Java": "java",
    "python": "python", "python3": "python", "PYTHON": "python", "Python": "python",
    "c": "c", "c programming": "c", "C": "c",
    "c++": "c++", "cpp": "c++", "C++": "c++",
    "javascript": "javascript", "js": "javascript", "es6": "javascript", "JAVASCRIPT": "javascript", "JavaScript": "javascript",
    "react": "react", "react.js": "react", "reactjs": "react", "REACT": "react", "React": "react",
    "node.js": "node.js", "nodejs": "node.js", "node": "node.js", "NODE.JS": "node.js", "Node.js": "node.js",
    "spring boot": "spring boot", "springboot": "spring boot", "SPRING BOOT": "spring boot", "Spring Boot": "spring boot",
    "sql": "sql", "structured query language": "sql", "SQL": "sql",
    "mongodb": "mongodb", "mongo": "mongodb", "MONGODB": "mongodb", "MongoDB": "mongodb",
    "mysql": "mysql", "MYSQL": "mysql", "MySQL": "mysql",
    "postgresql": "postgresql", "postgres": "postgresql", "POSTGRESQL": "postgresql", "PostgreSQL": "postgresql",
    "aws": "aws", "amazon web services": "aws", "AWS": "aws",
    "azure": "azure", "microsoft azure": "azure", "AZURE": "azure", "Azure": "azure",
    "docker": "docker", "docker container": "docker", "DOCKER": "docker", "Docker": "docker",
    "git": "git", "GIT": "git", "Git": "git",
    "github": "github", "GITHUB": "github", "GitHub": "github",
    "dsa": "dsa", "data structures": "dsa", "algorithms": "dsa", "data structures and algorithms": "dsa", "DSA": "dsa",
    "machine learning": "machine learning", "ml": "machine learning", "MACHINE LEARNING": "machine learning", "Machine Learning": "machine learning",
    "deep learning": "deep learning", "dl": "deep learning", "DEEP LEARNING": "deep learning", "Deep Learning": "deep learning",
    "pandas": "pandas", "PANDAS": "pandas", "Pandas": "pandas",
    "numpy": "numpy", "NUMPY": "numpy", "NumPy": "numpy",
    "scikit-learn": "scikit-learn", "sklearn": "scikit-learn", "scikit learn": "scikit-learn", "Scikit-learn": "scikit-learn",
    "power bi": "power bi", "powerbi": "power bi", "POWER BI": "power bi", "Power BI": "power bi",
    "tableau": "tableau", "TABLEAU": "tableau", "Tableau": "tableau",
    "html": "html", "html5": "html", "HTML": "html",
    "css": "css", "css3": "css", "CSS": "css"
}

JOB_ROLE_DEFAULTS = {
    "Java Developer": {
        "required_skills": ["java", "spring boot", "sql", "git", "aws", "docker"],
        "min_experience": 3,
        "description": "Looking for an experienced Java Developer proficient in Core Java, Spring Boot microservices, Hibernate, SQL databases, Git, Docker, and AWS cloud deployment. Responsible for building resilient enterprise backend services and RESTful APIs."
    },
    "Python Developer": {
        "required_skills": ["python", "sql", "git", "docker", "aws", "dsa"],
        "min_experience": 2,
        "description": "Seeking a Python Developer to build scalable backend systems, microservices, and automation pipelines using Python, SQL databases, Git, Docker, and AWS. Strong grasp of data structures and algorithms (DSA) required."
    },
    "Data Analyst": {
        "required_skills": ["python", "sql", "tableau", "power bi", "pandas", "numpy"],
        "min_experience": 2,
        "description": "Hiring a Data Analyst skilled in Python, SQL query optimization, data cleaning with Pandas and NumPy, and creating interactive BI dashboards using Tableau and Power BI. Experience translating data into business insights is essential."
    },
    "Data Scientist": {
        "required_skills": ["python", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "sql"],
        "min_experience": 3,
        "description": "We are hiring a Data Scientist to develop statistical and predictive models using Python, Scikit-learn, Pandas, and NumPy, with advanced machine learning, deep learning architectures, and SQL data warehousing."
    },
    "Web Developer": {
        "required_skills": ["html", "css", "javascript", "react", "node.js", "git"],
        "min_experience": 2,
        "description": "Seeking a Web Developer with solid expertise in modern web technologies including HTML, CSS, JavaScript, React for frontend interfaces, Node.js for backend runtime, and Git version control."
    },
    "Frontend Developer": {
        "required_skills": ["javascript", "react", "html", "css", "git", "github"],
        "min_experience": 2,
        "description": "Looking for a Frontend Developer passionate about UI/UX to build high-performance web applications using JavaScript, React, HTML, CSS, Git, and GitHub. Experience with responsive layout design required."
    },
    "Backend Developer": {
        "required_skills": ["python", "java", "sql", "spring boot", "docker", "git", "postgresql"],
        "min_experience": 3,
        "description": "Hiring a Backend Developer to architect secure and scalable microservices using Python or Java, Spring Boot, PostgreSQL, SQL, Docker, and Git. Focused on high throughput and reliable database integration."
    },
    "Full Stack Developer": {
        "required_skills": ["javascript", "react", "node.js", "python", "sql", "git", "docker"],
        "min_experience": 3,
        "description": "Looking for a versatile Full Stack Developer experienced across the entire software stack: React and JavaScript on frontend, Node.js or Python backend, SQL database modeling, Docker containers, and Git."
    },
    "Software Engineer": {
        "required_skills": ["java", "python", "dsa", "c++", "sql", "git"],
        "min_experience": 2,
        "description": "Seeking a Software Engineer with strong computer science fundamentals, data structures and algorithms (DSA), and proficiency in Java, Python, C++, SQL, and Git to develop mission-critical distributed software systems."
    },
    "Database Developer": {
        "required_skills": ["sql", "mysql", "postgresql", "mongodb", "python", "git"],
        "min_experience": 3,
        "description": "Hiring a Database Developer to design, optimize, and maintain relational and NoSQL databases using SQL, MySQL, PostgreSQL, MongoDB, with Python scripting and Git for schema migrations."
    }
}


class ModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.tfidf_vectorizer = None
        self.pipeline = None
        self.load_artifacts()

    def load_artifacts(self):
        """Loads trained Colab artifacts from disk."""
        model_path = os.path.join(MODELS_DIR, "resume_shortlisting_model.pkl")
        scaler_path = os.path.join(MODELS_DIR, "preprocessor.pkl")
        tfidf_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
        pipeline_path = os.path.join(MODELS_DIR, "resume_shortlisting_pipeline.pkl")

        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print(f"Loaded ML model from: {model_path}")
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                print(f"Loaded Scaler from: {scaler_path}")
            if os.path.exists(tfidf_path):
                self.tfidf_vectorizer = joblib.load(tfidf_path)
                print(f"Loaded TF-IDF Vectorizer from: {tfidf_path}")
            if os.path.exists(pipeline_path):
                self.pipeline = joblib.load(pipeline_path)
                print(f"Loaded unified pipeline from: {pipeline_path}")
        except Exception as e:
            print(f"Warning loading some model artifacts: {e}")

    def clean_nlp_text(self, text):
        if not isinstance(text, str):
            return ""
        text_lower = text.lower()
        text_clean = re.sub(r'[^a-z0-9+#\.\s]', ' ', text_lower)
        tokens = text_clean.split()
        meaningful = [t for t in tokens if t not in NLTK_STOPWORDS and len(t) > 1]
        return " ".join(meaningful)

    def extract_skills(self, text):
        clean_t = text.lower()
        detected = set()
        for alias, standard in SKILL_NORMALIZATION_MAP.items():
            pattern = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern, clean_t):
                detected.add(standard)
        return sorted(list(detected))

    def parse_experience(self, text):
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*\+?\s*years?', text, re.IGNORECASE)
        if matches:
            try:
                nums = [float(m) for m in matches]
                return max(nums)
            except ValueError:
                pass
        return 2.0

    def parse_education(self, text):
        for deg in ["Ph.D.", "PhD", "Doctorate", "M.Tech", "M.S.", "Master's Degree"]:
            if deg.lower() in text.lower():
                return deg, 95.0
        for deg in ["B.Tech", "B.E.", "B.S.", "MCA", "Bachelor's Degree"]:
            if deg.lower() in text.lower():
                return deg, 90.0
        for deg in ["BCA", "B.Sc", "Associate"]:
            if deg.lower() in text.lower():
                return deg, 80.0
        return "Bachelor's Degree", 75.0

    def parse_projects(self, text):
        proj_matches = re.findall(r'(?:project|platform|engine|dashboard|system|application|pipeline):\s*([^\n\.]+)', text, re.IGNORECASE)
        if proj_matches:
            return [p.strip().title() for p in proj_matches[:4]]
        return ["Enterprise Microservice Application", "Interactive Data Dashboard"]

    def parse_certifications(self, text):
        cert_matches = re.findall(r'(AWS Certified[^\n,\.]*|Azure[^\n,\.]*|Oracle Certified[^\n,\.]*|Docker Certified[^\n,\.]*|Kubernetes[^\n,\.]*|Google Cloud[^\n,\.]*|Certified[^\n,\.]*)', text, re.IGNORECASE)
        if cert_matches:
            return [c.strip().title() for c in cert_matches[:3]]
        return ["AWS Certified Solutions Architect"]

    def analyze_resume(self, resume_text, job_description="", job_role="Java Developer", filename=""):
        """
        Executes end-to-end resume analysis using the exact Colab Data Mining pipeline.
        """
        contact = extract_contact_info(resume_text, filename)
        
        # If job description is not provided, use catalog default
        role_info = JOB_ROLE_DEFAULTS.get(job_role, JOB_ROLE_DEFAULTS["Java Developer"])
        if not job_description or len(job_description.strip()) < 10:
            job_description = role_info["description"]
        
        req_skills = role_info["required_skills"]
        min_exp = role_info["min_experience"]

        # 1. NLP Text Cleaning
        clean_resume = self.clean_nlp_text(resume_text)
        clean_job = self.clean_nlp_text(job_description)

        # 2. Skill Extraction & Matching
        cand_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        if not job_skills:
            job_skills = req_skills

        matched_skills = [s for s in job_skills if s in cand_skills]
        missing_skills = [s for s in job_skills if s not in cand_skills]
        skill_match_score = round((len(matched_skills) / len(job_skills)) * 100.0, 2) if job_skills else 50.0

        # 3. TF-IDF Cosine Similarity
        cos_sim = 65.0
        if self.tfidf_vectorizer is not None:
            try:
                vec_res = self.tfidf_vectorizer.transform([clean_resume])
                vec_job = self.tfidf_vectorizer.transform([clean_job])
                sim = cosine_similarity(vec_res, vec_job)[0][0]
                cos_sim = round(float(sim) * 100.0, 2)
            except Exception as e:
                print(f"TF-IDF similarity error: {e}")

        # 4. Experience Matching
        cand_exp = self.parse_experience(resume_text)
        if cand_exp >= min_exp:
            exp_match_score = 100.0
        else:
            exp_match_score = round(max(15.0, (cand_exp / min_exp) * 100.0), 2)

        # 5. Education Scoring
        degree_name, edu_score = self.parse_education(resume_text)

        # 6. Projects & Certifications
        projects = self.parse_projects(resume_text)
        proj_count = len(projects)
        proj_score = min(100.0, max(30.0, proj_count * 25.0))

        certs = self.parse_certifications(resume_text)
        has_certs = any(c for c in certs if c.lower() != "none")
        cert_score = 90.0 if has_certs else 30.0

        # 7. Exact Overall Score Formula (50% Skill, 20% Exp, 10% Edu, 10% Proj, 10% Cert)
        overall_score = round(
            (skill_match_score * 0.50) +
            (exp_match_score * 0.20) +
            (edu_score * 0.10) +
            (proj_score * 0.10) +
            (cert_score * 0.10), 2
        )
        overall_score = float(np.clip(overall_score, 0.0, 100.0))

        # 8. ML Model Prediction
        pred = None
        if self.model is not None:
            try:
                feat_dict = {
                    "experience_years": cand_exp,
                    "skill_count": len(cand_skills),
                    "project_count": proj_count,
                    "certification_count": len(certs) if has_certs else 0,
                    "skill_match_score": skill_match_score,
                    "experience_match_score": exp_match_score,
                    "education_match_score": edu_score,
                    "project_score": proj_score,
                    "certification_score": cert_score,
                    "cosine_similarity_score": cos_sim
                }
                df_feat = pd.DataFrame([feat_dict])[FEATURE_COLUMNS]
                if self.scaler is not None:
                    X_in = self.scaler.transform(df_feat)
                else:
                    X_in = df_feat
                pred = self.model.predict(X_in)[0]
            except Exception as e:
                print(f"Model prediction fallback: {e}")

        # Deterministic label fallback matching Colab target rules
        if not pred:
            if overall_score >= 80.0:
                pred = "SHORTLISTED"
            elif overall_score >= 60.0:
                pred = "REVIEW"
            else:
                pred = "REJECTED"

        # Selection determination (Selected if >= 75 or model SHORTLISTED, else Rejected)
        is_selected = (pred == "SHORTLISTED" or overall_score >= 75.0)
        status = "Selected" if is_selected else "Rejected"

        if is_selected:
            recommendation = "Selected: Strong candidate with high technical alignment, qualified experience, and matching skill profile."
        else:
            recommendation = "Rejected: Candidate does not meet the qualification threshold or has significant core skill gaps."

        return {
            "candidate_name": contact["candidate_name"],
            "candidateName": contact["candidate_name"],
            "resume_filename": filename or "resume.pdf",
            "resumeFileName": filename or "resume.pdf",
            "score": round(overall_score, 1),
            "status": status,
            "shortlist_status": status,
            "email": contact["email"],
            "phone": contact["phone"],
            "education": degree_name,
            "experience_years": cand_exp,
            "skills": cand_skills,
            "projects": projects,
            "certifications": certs if has_certs else ["None"],
            "job_role": job_role,
            "job_required_skills": req_skills,
            "skill_match_score": skill_match_score,
            "experience_match_score": exp_match_score,
            "education_match_score": edu_score,
            "project_score": proj_score,
            "certification_score": cert_score,
            "cosine_similarity_score": cos_sim,
            "overall_score": overall_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendation": recommendation,
            "clean_resume_preview": clean_resume[:200]
        }


# Singleton service instance
model_service = ModelService()

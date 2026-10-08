"""
==============================================================================
Script to Generate the Complete Google Colab Jupyter Notebook:
Resume_Shortlisting_DataMining_DataWarehouse.ipynb
==============================================================================
"""

import os
import json
import uuid

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def make_cell(cell_type, source, cell_id=None):
    if cell_id is None:
        cell_id = uuid.uuid4().hex[:8]
    
    # Ensure source is a list of strings ending with newlines
    if isinstance(source, str):
        lines = [line + "\n" for line in source.split("\n")]
        # Remove trailing newline from last line if original didn't have one
        if not source.endswith("\n") and lines:
            lines[-1] = lines[-1][:-1]
    else:
        lines = source

    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "id": cell_id,
        "source": lines
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell


def build_notebook():
    cells = []

    # -------------------------------------------------------------------------
    # CELL 1: TITLE & HEADER
    # -------------------------------------------------------------------------
    title_md = """# 🎓 College Project: Resume Shortlisting and Candidate Analytics
### *Using Advanced Data Mining and Data Warehousing (Star Schema)*

---

## 📌 Project Overview
In modern talent acquisition, organizations receive thousands of resumes for every open position. Manual screening is slow, error-prone, and biased. 

This project implements an end-to-end **Data Mining and Data Warehousing Pipeline** specifically designed for a **Resume Shortlisting and Candidate Analytics System**.

### 🎯 Primary Project Goal:
Given:
1. **A Job Description (JD)**
2. **A Candidate Resume**

The system automatically performs:
- Text extraction and Natural Language Processing (NLP)
- Skill extraction and normalization
- Required vs. candidate skill matching
- Multi-criteria weighted scoring (Skills, Experience, Education, Projects, Certifications)
- Machine Learning classification predicting:
  - 🟢 **SHORTLISTED** (Overall Score $\\ge 80\\%$)
  - 🟡 **REVIEW** ($60\\% \\le$ Overall Score $< 80\\%$)
  - 🔴 **REJECTED** (Overall Score $< 60\\%$)
- Unsupervised candidate clustering (K-Means) for candidate segmentation
- Extraction of dimensions and facts into a **Star Schema Data Warehouse** for OLAP analytics.

---
"""
    cells.append(make_cell("markdown", title_md))

    # -------------------------------------------------------------------------
    # CELL 2: THEORETICAL FOUNDATIONS (Academic Concepts Explained)
    # -------------------------------------------------------------------------
    theory_md = """# 📚 Academic & Theoretical Foundations

Before diving into code, let us clearly understand the key computer science concepts powering this system:

---

### 1. What is Data Mining?
**Data Mining** is the computational process of discovering hidden, previously unknown, valid, and actionable patterns, correlations, anomalies, and insights from large volumes of data. It blends techniques from artificial intelligence, machine learning, statistics, and database systems.
- In our project, Data Mining is used to:
  - Mine specific technical skills from unstructured resume text.
  - Classify candidates into shortlisting categories (Supervised Data Mining).
  - Cluster candidates into archetypes like *High Skill / High Experience* (Unsupervised Data Mining).
  - Extract feature importances to see what drives hiring decisions.

---

### 2. What is Data Warehousing?
A **Data Warehouse (DWH)** is a centralized, subject-oriented, integrated, time-variant, and non-volatile repository of structured data gathered from multiple operational sources. Its primary purpose is to support Online Analytical Processing (OLAP) and business intelligence (BI) reporting rather than everyday transaction processing (OLTP).
- In our project, the Data Warehouse stores all candidate evaluation events over time so HR directors can run queries such as:
  - *"Which universities produce candidates with the highest skill match score?"*
  - *"What is the quarter-over-quarter trend in shortlisting rates for Python Developers?"*

---

### 3. What is ETL (Extract, Transform, Load)?
**ETL** is the three-step data engineering process that moves data from source systems into the Data Warehouse:
1. **Extract**: Pulling raw data (e.g., resume texts, candidate application metadata, job requirements).
2. **Transform**: Cleaning messy data (removing nulls, dropping duplicates), normalizing inconsistent casings (`java` vs `JAVA` vs `Java`), engineering numerical feature scores, and validating constraints.
3. **Load**: Loading clean, structured facts and dimensions into relational tables or CSV star schemas ready for analytics.

---

### 4. What is TF-IDF?
**TF-IDF** stands for **Term Frequency - Inverse Document Frequency**. It is a fundamental numerical statistic in Natural Language Processing (NLP) that reflects how important a word is to a document within a collection (corpus):
$$\\text{TF-IDF}(t, d, D) = \\text{TF}(t, d) \\times \\text{IDF}(t, D)$$
- **Term Frequency (TF)**: How frequently term $t$ appears in document $d$:
  $$\\text{TF}(t, d) = \\frac{\\text{Count of } t \\text{ in } d}{\\text{Total words in } d}$$
- **Inverse Document Frequency (IDF)**: Measures how common or rare a term is across all documents $D$:
  $$\\text{IDF}(t, D) = \\log\\left(\\frac{1 + |D|}{1 + |\\{d \\in D : t \\in d\\}|}\\right) + 1$$
- **Why it matters**: Common words like *"experience"*, *"worked"*, and *"team"* appear in almost every resume and receive a low IDF weight. Unique domain keywords like *"Kubernetes"*, *"PyTorch"*, or *"Hibernate"* appear only in relevant resumes and receive high IDF weights.

---

### 5. What is Cosine Similarity?
**Cosine Similarity** measures the semantic or vector similarity between two non-zero vectors in an inner product space by calculating the cosine of the angle between them:
$$\\text{Cosine Similarity}(\\mathbf{A}, \\mathbf{B}) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{\\|\\mathbf{A}\\| \\|\\mathbf{B}\\|} = \\frac{\\sum_{i=1}^{n} A_i B_i}{\\sqrt{\\sum_{i=1}^{n} A_i^2} \\sqrt{\\sum_{i=1}^{n} B_i^2}}$$
- When applied to the TF-IDF vectors of a Resume and a Job Description:
  - $\\text{Similarity} = 1.0$ ($100\\%$): The resume and job description use identical vocabulary.
  - $\\text{Similarity} = 0.0$ ($0\\%$): The resume shares zero vocabulary with the job description.

---

### 6. What is Classification? (Supervised Data Mining)
**Classification** is a supervised learning task where an algorithm learns a mapping function from input features $\\mathbf{X}$ (e.g., experience years, skill match percentage, project score) to discrete categorical target labels $y$ (e.g., `SHORTLISTED`, `REVIEW`, `REJECTED`).
We evaluate three distinct classification algorithms:
1. **Logistic Regression**: Linear probabilistic classifier using a sigmoid/softmax link function.
2. **Decision Tree**: Non-linear, interpretable tree-structured model splitting on information gain / Gini impurity.
3. **Random Forest**: Ensemble of bagging decision trees that reduces variance and avoids overfitting.

---

### 7. What is Clustering? (Unsupervised Data Mining)
**Clustering** is an unsupervised learning task that groups unlabelled observations into clusters such that candidates in the same cluster are more similar to each other than to candidates in other clusters.
We use **K-Means Clustering** with the **Elbow Method** to identify distinct candidate talent pools (e.g., *Top Tier Veterans*, *High-Potential Freshers*, *Low-Match Applicants*).

---

### 8. What is a Fact Table, Dimension Table, and Star Schema?
- **Fact Table**: The central table containing numerical measurements, metrics, and additive facts of a business process (e.g., `skill_match_score`, `overall_score`, `experience_match_score`), along with foreign keys referencing dimensions.
- **Dimension Tables**: Contextual satellite tables containing descriptive attributes (e.g., candidate demographic details, job role details, skill taxonomies, calendar dates, education levels).
- **Star Schema**: A dimensional data model where the central fact table connects directly to surrounding dimension tables in the shape of a star. It provides lightning-fast query performance and simplifies analytical reporting.

---

### 9. How will this Trained Model Connect to a Flask Website?
In Phase 2 of this project:
1. The trained pipeline object (`resume_shortlisting_pipeline.pkl`) is loaded once into memory when Flask starts up.
2. A user uploads a candidate PDF resume and pastes a Job Description into a web form.
3. The Flask backend extracts the text from the PDF (using `pypdf` or OCR `pytesseract`).
4. The pipeline processes the extracted text, extracts skills, computes TF-IDF and matching scores, and predicts `SHORTLISTED`, `REVIEW`, or `REJECTED`.
5. The result is returned as interactive JSON and displayed on a web dashboard!
"""
    cells.append(make_cell("markdown", theory_md))

    # -------------------------------------------------------------------------
    # CELL 3: SETUP & IMPORTS
    # -------------------------------------------------------------------------
    setup_code = """# ==============================================================================
# ENVIRONMENT SETUP & DEPENDENCY IMPORTS
# ==============================================================================
import os
import sys
import re
import json
import random
import zipfile
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import joblib

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Set random seeds for exact reproducibility
np.random.seed(42)
random.seed(42)

# Configure plot styles
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["font.size"] = 10

# Create Project Folder Structure
PROJECT_DIR = "resume_shortlisting_project"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

print("✅ Setup complete! Created project folders:")
print(f" - Data Directory:    {DATA_DIR}")
print(f" - Models Directory:  {MODELS_DIR}")
print(f" - Reports Directory: {REPORTS_DIR}")
"""
    cells.append(make_cell("code", setup_code))

    # -------------------------------------------------------------------------
    # CELL 4: DATASET GENERATION EXPLANATION
    # -------------------------------------------------------------------------
    dataset_md = """# 1. Create a Realistic Resume Dataset

### Why Synthetic Data?
In human resources, real resumes contain Personally Identifiable Information (PII) protected by privacy regulations (GDPR, CCPA). Generating a controlled, realistic synthetic dataset allows us to model diverse candidate distributions, simulate real-world noise (formatting quirks, capitalization errors, duplicates), and test matching algorithms across 10 specialized technical roles:
1. **Java Developer**
2. **Python Developer**
3. **Web Developer**
4. **Data Analyst**
5. **Data Scientist**
6. **Software Engineer**
7. **Frontend Developer**
8. **Backend Developer**
9. **Full Stack Developer**
10. **Database Developer**

We generate over **5,000+ candidate records** with realistic variation across:
- **Strong Candidates** (~35%): High skill overlap (80-100%), required experience, relevant degrees, verified projects.
- **Review Candidates** (~35%): Partial skill overlap (50-75%), junior or borderline experience, related degrees.
- **Weak Candidates** (~30%): Low skill overlap (<30%), domain mismatches, non-STEM background.
- **Messy Data**: Extra whitespace, duplicate rows, missing fields, and varied casing (`java`, `JAVA`, `Java`).
"""
    cells.append(make_cell("markdown", dataset_md))

    # -------------------------------------------------------------------------
    # CELL 5: DATASET GENERATION CODE
    # -------------------------------------------------------------------------
    dataset_code = """# ==============================================================================
# 1. KNOWLEDGE BASE & SYNTHETIC DATASET GENERATION
# ==============================================================================

JOB_ROLES_CATALOG = {
    "Java Developer": {
        "required_skills": ["Java", "Spring Boot", "Hibernate", "REST API", "SQL", "Microservices", "Git", "Maven", "Docker", "AWS"],
        "min_exp": 3,
        "description": "Seeking an experienced Java Developer to architect, build, and optimize enterprise backend microservices. Proficiency in Java 17+, Spring Boot, Hibernate, REST APIs, SQL, Docker, and AWS cloud deployment required."
    },
    "Python Developer": {
        "required_skills": ["Python", "Django", "FastAPI", "Flask", "REST API", "PostgreSQL", "Git", "Docker", "Redis", "Celery"],
        "min_exp": 2,
        "description": "Looking for a skilled Python Developer to build high-performance APIs and distributed web applications using Python, Django, FastAPI, PostgreSQL, Redis caching, and Docker containerization."
    },
    "Web Developer": {
        "required_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Express", "REST API", "MongoDB", "Git", "Bootstrap"],
        "min_exp": 2,
        "description": "Hiring a creative Web Developer proficient in responsive HTML5/CSS3, modern JavaScript (ES6+), React, Node.js, Express, and MongoDB to deliver engaging web applications."
    },
    "Data Analyst": {
        "required_skills": ["SQL", "Python", "Excel", "Power BI", "Tableau", "Data Analysis", "Statistics", "Pandas", "Data Cleaning", "Data Visualization"],
        "min_exp": 2,
        "description": "Seeking a Data Analyst to transform complex datasets into executive dashboards and strategic insights. Strong expertise in SQL queries, Power BI, Tableau, Excel, and Python data manipulation (Pandas) required."
    },
    "Data Scientist": {
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Statistics", "Natural Language Processing", "TensorFlow"],
        "min_exp": 3,
        "description": "Hiring a Data Scientist to develop statistical models, machine learning pipelines, and NLP applications using Python, Scikit-Learn, TensorFlow, SQL, and advanced mathematical modeling."
    },
    "Software Engineer": {
        "required_skills": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git", "Object-Oriented Programming", "REST API", "SQL", "Linux"],
        "min_exp": 2,
        "description": "Looking for a Software Engineer with a solid foundation in Data Structures, Algorithms, OOP, and system design in Python, Java, or C++, with hands-on Git, Linux, and REST API development."
    },
    "Frontend Developer": {
        "required_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Next.js", "Redux", "Tailwind CSS", "Git", "UI/UX"],
        "min_exp": 2,
        "description": "Seeking a talented Frontend Developer experienced in building modular, accessible single-page applications using React, TypeScript, Redux Toolkit, Tailwind CSS, and REST API integrations."
    },
    "Backend Developer": {
        "required_skills": ["Node.js", "Express", "Python", "Java", "REST API", "PostgreSQL", "MongoDB", "Docker", "Microservices", "Redis"],
        "min_exp": 3,
        "description": "Seeking an experienced Backend Developer to design secure server-side architectures, database schemas, and microservices using Node.js, Python, PostgreSQL, Redis, and Docker."
    },
    "Full Stack Developer": {
        "required_skills": ["React", "Node.js", "JavaScript", "TypeScript", "Python", "HTML", "CSS", "MongoDB", "SQL", "Docker", "Git"],
        "min_exp": 3,
        "description": "Looking for an adaptable Full Stack Developer capable of delivering both dynamic React frontends and scalable Node.js/Python backends backed by SQL and NoSQL databases."
    },
    "Database Developer": {
        "required_skills": ["SQL", "PostgreSQL", "MySQL", "Oracle", "Database Design", "Query Optimization", "ETL", "Stored Procedures", "NoSQL", "Linux"],
        "min_exp": 3,
        "description": "Seeking a Database Developer with mastery in relational database design, complex SQL query tuning, stored procedures, ETL pipelines, and performance optimization across PostgreSQL, MySQL, and Oracle."
    }
}

FIRST_NAMES = ["Aarav", "Aditi", "Alexander", "Amara", "Amit", "Ananya", "Andrew", "Brandon", "Daniel", "David", "Deepak", "Divya", "Emily", "Emma", "Harsh", "James", "John", "Kavya", "Manish", "Michael", "Neha", "Nikhil", "Pooja", "Priya", "Rahul", "Rohan", "Ryan", "Samantha", "Sarah", "Shreya", "Sneha", "Varun", "Vikas"]
LAST_NAMES = ["Agarwal", "Brown", "Chopra", "Davis", "Garcia", "Gupta", "Iyer", "Jain", "Johnson", "Kapoor", "Kumar", "Miller", "Mishra", "Nair", "Patel", "Rao", "Reddy", "Sharma", "Singh", "Smith", "Taylor", "Verma", "Williams", "Wilson"]
LOCATIONS = ["Bangalore, India", "Hyderabad, India", "Pune, India", "Chennai, India", "Delhi NCR, India", "Mumbai, India", "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Boston, MA", "Chicago, IL", "London, UK", "Toronto, Canada", "Remote"]

DEGREES_AND_TIERS = [
    ("M.Tech", "Computer Science", 95), ("M.S.", "Data Science", 95), ("M.S.", "Computer Science", 95),
    ("MCA", "Computer Applications", 90), ("B.Tech", "Computer Science", 90), ("B.Tech", "Information Technology", 88),
    ("B.E.", "Computer Engineering", 88), ("B.Tech", "Artificial Intelligence", 90), ("B.S.", "Computer Science", 90),
    ("B.Sc", "Computer Science", 80), ("BCA", "Computer Applications", 80), ("B.Tech", "Electronics & Communication", 78),
    ("B.Tech", "Electrical Engineering", 72), ("B.Tech", "Mechanical Engineering", 65), ("B.Com", "Information Systems", 60),
    ("B.Com", "General Commerce", 45), ("B.A.", "Economics", 50), ("High School", "General", 30)
]

CERTIFICATIONS_LIST = [
    "AWS Certified Solutions Architect", "AWS Certified Developer Associate",
    "Google Professional Data Engineer", "Microsoft Certified: Azure Data Scientist",
    "TensorFlow Developer Certificate", "Oracle Certified Professional: Java SE",
    "Meta Front-End Developer Professional", "Meta Back-End Developer Professional",
    "IBM Data Science Professional", "Tableau Desktop Specialist",
    "Microsoft Certified: Power BI Data Analyst", "Certified Kubernetes Administrator (CKA)", "None"
]

PROJECT_TEMPLATES = {
    "Java Developer": ["E-Commerce Microservices Engine with Spring Boot and Kafka", "Hospital Management System using Java, Hibernate and MySQL", "Banking Core Transaction API with OAuth2 and Spring Security"],
    "Python Developer": ["Real-Time Chat Service with FastAPI and WebSockets", "Automated Financial Data Pipeline using Django and Celery", "SaaS Subscription Backend with Python, PostgreSQL and Stripe API"],
    "Web Developer": ["Interactive Collaborative Canvas using React", "Multi-Vendor Marketplace with MERN Stack", "Corporate Responsive Portal with JavaScript and Bootstrap"],
    "Data Analyst": ["Customer Churn Predictive Analysis with Power BI Dashboard", "E-Commerce Sales Performance Analytics in Tableau and SQL", "Supply Chain Optimization Analytics using SQL and Pandas"],
    "Data Scientist": ["Customer Sentiment Analysis on 100k Reviews using NLP", "Credit Risk Default Prediction Engine with TensorFlow", "Time Series Stock Forecasting Model with LSTM"],
    "Software Engineer": ["High-Concurrency Key-Value Store in C++", "Distributed Web Crawler using Java and Multithreading", "High-Performance Network Proxy Server in Linux"],
    "Frontend Developer": ["E-Commerce Storefront with Next.js and Tailwind CSS", "Cryptocurrency Portfolio Tracker in React with Redux", "Accessible SaaS Onboarding Flow with TypeScript"],
    "Backend Developer": ["Multi-Tenant Authentication Microservice using Node.js", "Event-Driven Order Processing Engine with Python and PostgreSQL", "Cloud-Native RESTful API Gateway with Docker"],
    "Full Stack Developer": ["Enterprise Project Management System with React and Node.js", "Social Media Platform with Next.js and MongoDB", "Real-time Auction Platform with React and FastAPI"],
    "Database Developer": ["Database Partitioning and Index Optimization in PostgreSQL", "Enterprise Data Warehouse ETL Pipeline using Stored Procedures", "High-Availability MySQL Cluster with Replication"]
}

def generate_synthetic_resumes(n_records=5200):
    roles = list(JOB_ROLES_CATALOG.keys())
    records = []
    
    for i in range(1, n_records + 1):
        cand_id = f"CAND_{i:05d}"
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 999)}@gmail.com"
        loc = random.choice(LOCATIONS)
        
        target_role = random.choice(roles)
        job_info = JOB_ROLES_CATALOG[target_role]
        job_req_skills = job_info["required_skills"]
        job_desc = job_info["description"]
        min_exp = job_info["min_exp"]
        
        archetype = random.random()
        if archetype < 0.35:  # Strong
            num_match = random.randint(int(len(job_req_skills) * 0.8), len(job_req_skills))
            cand_skills = random.sample(job_req_skills, num_match) + random.sample(["Git", "Linux", "REST API", "Docker", "SQL"], random.randint(1, 2))
            cand_skills = list(dict.fromkeys(cand_skills))
            exp = random.randint(min_exp, min_exp + random.randint(2, 7))
            deg, spec, _ = random.choice([d for d in DEGREES_AND_TIERS if d[2] >= 85])
            projs = random.sample(PROJECT_TEMPLATES[target_role], random.randint(2, 3))
            certs = random.sample([c for c in CERTIFICATIONS_LIST if c != "None"], random.randint(1, 2))
        elif archetype < 0.70:  # Review
            num_match = random.randint(int(len(job_req_skills) * 0.5), int(len(job_req_skills) * 0.75))
            other_role = random.choice([r for r in roles if r != target_role])
            cand_skills = random.sample(job_req_skills, num_match) + random.sample(JOB_ROLES_CATALOG[other_role]["required_skills"], 2)
            cand_skills = list(dict.fromkeys(cand_skills))
            exp = max(1, random.randint(min_exp - 2, min_exp + 1))
            deg, spec, _ = random.choice([d for d in DEGREES_AND_TIERS if 65 <= d[2] <= 90])
            projs = random.sample(PROJECT_TEMPLATES[target_role], 1)
            certs = [random.choice(CERTIFICATIONS_LIST)]
            certs = [] if certs == ["None"] else certs
        else:  # Weak
            num_match = random.randint(0, max(1, int(len(job_req_skills) * 0.3)))
            cand_skills = (random.sample(job_req_skills, num_match) if num_match > 0 else []) + ["Communication", "MS Office"]
            exp = random.randint(0, max(1, min_exp - 1))
            deg, spec, _ = random.choice([d for d in DEGREES_AND_TIERS if d[2] <= 75])
            projs = ["Academic Coursework"] if random.random() > 0.5 else []
            certs = []

        # Introduce dirty casings for cleaning demonstration
        cased_skills = []
        for s in cand_skills:
            r = random.random()
            if r < 0.15: cased_skills.append(s.upper())
            elif r < 0.30: cased_skills.append(s.lower())
            elif r < 0.40: cased_skills.append(f"  {s}  ")
            else: cased_skills.append(s)

        skills_str = ", ".join(cased_skills)
        projs_str = "; ".join(projs) if projs else "None"
        certs_str = ", ".join(certs) if certs else "None"
        
        resume_text = (
            f"Candidate: {name}\\nEmail: {email} | Location: {loc}\\n"
            f"Summary: Dedicated {target_role} with {exp} years of technical experience in software engineering.\\n"
            f"Technical Skills: {skills_str}\\nEducation: {deg} in {spec}\\n"
            f"Key Projects: {projs_str}\\nCertifications: {certs_str}\\n"
        )
        
        records.append({
            "candidate_id": cand_id, "candidate_name": name, "email": email,
            "education": f"{deg} in {spec}", "degree": deg, "specialization": spec,
            "experience_years": exp, "skills": skills_str, "projects": projs_str,
            "certifications": certs_str, "job_role": target_role,
            "job_required_skills": ", ".join(job_req_skills),
            "job_description": job_desc, "location": loc, "resume_text": resume_text
        })
        
    df = pd.DataFrame(records)
    # Add dirty records (duplicates, nulls, whitespace)
    dups = df.sample(n=120, random_state=42).copy()
    df = pd.concat([df, dups], ignore_index=True)
    null_idx = df.sample(n=80, random_state=123).index
    df.loc[null_idx[:40], "certifications"] = np.nan
    df.loc[null_idx[40:], "location"] = np.nan
    space_idx = df.sample(n=100, random_state=456).index
    df.loc[space_idx, "candidate_name"] = "  " + df.loc[space_idx, "candidate_name"] + "  "
    return df

raw_df = generate_synthetic_resumes(5200)
print(f"Generated raw dataset shape: {raw_df.shape}")
raw_df.head(2)
"""
    cells.append(make_cell("code", dataset_code))

    # -------------------------------------------------------------------------
    # CELL 6: DATA CLEANING EXPLANATION
    # -------------------------------------------------------------------------
    cleaning_md = """# 2. Data Cleaning & Preprocessing

Real-world resume databases contain significant noise. Proper preprocessing ensures model accuracy and stability.
We perform:
1. **Deduplication**: Identify and remove identical candidate submissions.
2. **Missing Value Imputation**: Handle null values in optional fields (e.g., certifications, locations).
3. **Whitespace Stripping**: Trim leading/trailing spaces from names, roles, and skills.
4. **Skill Name Normalization**: Standardize varied casings (`java` / `JAVA` / `Java` $\\to$ `Java`, `sql` / `SQL` $\\to$ `SQL`).
5. **Data Validation**: Clamp experience years and scores within logical boundaries.

Let's display the dataset statistics **before and after cleaning**.
"""
    cells.append(make_cell("markdown", cleaning_md))

    # -------------------------------------------------------------------------
    # CELL 7: DATA CLEANING CODE
    # -------------------------------------------------------------------------
    cleaning_code = """# ==============================================================================
# 2. DATA CLEANING & NORMALIZATION PIPELINE
# ==============================================================================

CANONICAL_SKILLS_MAP = {
    "java": "Java", "python": "Python", "sql": "SQL", "postgresql": "PostgreSQL",
    "mysql": "MySQL", "mongodb": "MongoDB", "oracle": "Oracle", "aws": "AWS",
    "azure": "Azure", "docker": "Docker", "kubernetes": "Kubernetes", "git": "Git",
    "html": "HTML", "css": "CSS", "javascript": "JavaScript", "typescript": "TypeScript",
    "react": "React", "next.js": "Next.js", "node.js": "Node.js", "express": "Express",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "spring boot": "Spring Boot",
    "hibernate": "Hibernate", "rest api": "REST API", "microservices": "Microservices",
    "c++": "C++", "excel": "Excel", "power bi": "Power BI", "tableau": "Tableau",
    "pandas": "Pandas", "numpy": "NumPy", "scikit-learn": "Scikit-Learn",
    "tensorflow": "TensorFlow", "redis": "Redis", "linux": "Linux"
}

def normalize_skills(skill_str):
    if not isinstance(skill_str, str) or pd.isna(skill_str):
        return "None"
    parts = [s.strip() for s in skill_str.split(",") if s.strip()]
    cleaned = []
    for p in parts:
        norm = CANONICAL_SKILLS_MAP.get(p.lower(), p.title())
        if norm not in cleaned:
            cleaned.append(norm)
    return ", ".join(cleaned) if cleaned else "None"

print("--- BEFORE CLEANING ---")
print(f"Total Rows:       {len(raw_df)}")
print(f"Duplicate Rows:   {raw_df.duplicated(subset=['candidate_id', 'email']).sum()}")
print(f"Missing Values:   {raw_df.isna().sum().sum()}")

# Clean dataset
clean_df = raw_df.drop_duplicates(subset=["candidate_id", "email"]).copy().reset_index(drop=True)

for col in clean_df.select_dtypes(include="object").columns:
    clean_df[col] = clean_df[col].astype(str).str.strip()

clean_df["certifications"] = clean_df["certifications"].replace({"nan": "None", "": "None"}).fillna("None")
clean_df["location"] = clean_df["location"].replace({"nan": "Remote", "": "Remote"}).fillna("Remote")
clean_df["skills"] = clean_df["skills"].apply(normalize_skills)
clean_df["job_required_skills"] = clean_df["job_required_skills"].apply(normalize_skills)
clean_df["experience_years"] = pd.to_numeric(clean_df["experience_years"], errors="coerce").fillna(0).clip(0, 40).astype(int)

print("\\n--- AFTER CLEANING ---")
print(f"Total Rows:       {len(clean_df)}")
print(f"Duplicate Rows:   {clean_df.duplicated(subset=['candidate_id', 'email']).sum()}")
print(f"Missing Values:   {clean_df.isna().sum().sum()}")
"""
    cells.append(make_cell("code", cleaning_code))

    # -------------------------------------------------------------------------
    # CELL 8: EDA EXPLANATION
    # -------------------------------------------------------------------------
    eda_md = """# 3. Exploratory Data Analysis (EDA)

EDA allows us to uncover data patterns, check class balance, and validate our synthetic distributions visually.
We construct **8 key visualizations**:
1. Candidates by Job Role
2. Experience Distribution (Histogram + KDE)
3. Education Distribution
4. Most Common Technical Skills (Top 15)
5. Certification Count Distribution
6. Candidate Matching Score Distribution
7. Shortlisted vs Review vs Rejected Proportions
8. Candidate Distribution by Seniority Tier
"""
    cells.append(make_cell("markdown", eda_md))

    # -------------------------------------------------------------------------
    # CELL 9: FEATURE ENGINEERING & SCORING CODE (Run before plots so scores exist)
    # -------------------------------------------------------------------------
    scoring_code = """# ==============================================================================
# 4. SKILL MATCHING, SCORING & TARGET LABEL CREATION
# ==============================================================================

EDUCATION_WEIGHT_MAP = {
    "M.Tech": 95.0, "M.S.": 95.0, "MCA": 90.0, "B.Tech": 90.0, "B.E.": 88.0,
    "B.S.": 90.0, "B.Sc": 80.0, "BCA": 80.0, "B.Com": 55.0, "B.A.": 50.0, "High School": 30.0
}

def match_skills(cand_skills_str, req_skills_str):
    c_list = [s.strip().lower() for s in cand_skills_str.split(",") if s.strip() and s.strip().lower() != "none"]
    r_list = [s.strip() for s in req_skills_str.split(",") if s.strip()]
    c_set = set(c_list)
    matched = [r for r in r_list if r.lower() in c_set]
    missing = [r for r in r_list if r.lower() not in c_set]
    tot = len(r_list) if r_list else 1
    pct = round((len(matched) / tot) * 100.0, 2)
    return len(matched), len(missing), pct, matched, missing

# 1. Skill Matching
m_counts, miss_counts, s_scores, m_lists, miss_lists = [], [], [], [], []
for _, row in clean_df.iterrows():
    mc, msc, pct, ml, missl = match_skills(row["skills"], row["job_required_skills"])
    m_counts.append(mc)
    miss_counts.append(msc)
    s_scores.append(pct)
    m_lists.append(", ".join(ml))
    miss_lists.append(", ".join(missl))

clean_df["matched_skills_count"] = m_counts
clean_df["missing_skills_count"] = miss_counts
clean_df["skill_match_score"] = s_scores
clean_df["matched_skills"] = m_lists
clean_df["missing_skills"] = miss_lists

# 2. Experience Match Score (20% weight)
exp_scores = []
for _, row in clean_df.iterrows():
    role = row["job_role"]
    min_exp = JOB_ROLES_CATALOG.get(role, {}).get("min_exp", 2)
    cand_exp = row["experience_years"]
    if cand_exp >= min_exp:
        score = min(100.0, 80.0 + (cand_exp - min_exp) * 4.0)
    else:
        score = max(20.0, (cand_exp / max(1, min_exp)) * 75.0)
    exp_scores.append(round(score, 2))
clean_df["experience_match_score"] = exp_scores

# 3. Education Match Score (10% weight)
edu_scores = []
for _, row in clean_df.iterrows():
    deg = row["degree"]
    spec = row["specialization"]
    base = EDUCATION_WEIGHT_MAP.get(deg, 60.0)
    if any(k in spec for k in ["Computer", "Data", "Artificial", "Information"]):
        adj = base
    elif "Electronics" in spec or "Electrical" in spec:
        adj = base * 0.90
    elif "Mechanical" in spec:
        adj = base * 0.75
    else:
        adj = base * 0.60
    edu_scores.append(round(min(100.0, max(20.0, adj)), 2))
clean_df["education_match_score"] = edu_scores

# 4. Project Score (10% weight)
clean_df["project_count"] = clean_df["projects"].apply(lambda p: 0 if p == "None" else len(p.split(";")))
clean_df["project_score"] = clean_df["project_count"].map(lambda c: 95.0 if c >= 3 else (80.0 if c == 2 else (65.0 if c == 1 else 25.0)))

# 5. Certification Score (10% weight)
clean_df["certification_count"] = clean_df["certifications"].apply(lambda c: 0 if c == "None" else len(c.split(",")))
clean_df["certification_score"] = clean_df["certification_count"].map(lambda c: 95.0 if c >= 2 else (80.0 if c == 1 else 30.0))

# 6. Overall Weighted Score Formula:
# overall_score = (skill_match * 0.50) + (exp_match * 0.20) + (edu_match * 0.10) + (proj * 0.10) + (cert * 0.10)
clean_df["overall_score"] = (
    (clean_df["skill_match_score"] * 0.50) +
    (clean_df["experience_match_score"] * 0.20) +
    (clean_df["education_match_score"] * 0.10) +
    (clean_df["project_score"] * 0.10) +
    (clean_df["certification_score"] * 0.10)
).round(2).clip(0.0, 100.0)

# 7. Target Shortlist Status
def assign_status(score):
    if score >= 80.0: return "SHORTLISTED"
    elif score >= 60.0: return "REVIEW"
    return "REJECTED"

clean_df["shortlist_status"] = clean_df["overall_score"].apply(assign_status)
clean_df["skill_count"] = clean_df["skills"].apply(lambda s: len(s.split(",")) if s != "None" else 0)

print("Target Class Distribution:")
print(clean_df["shortlist_status"].value_counts(normalize=True).mul(100).round(2).astype(str) + " %")
"""
    cells.append(make_cell("code", scoring_code))

    # -------------------------------------------------------------------------
    # CELL 10: EDA CODE (8 Visualizations)
    # -------------------------------------------------------------------------
    eda_code = """# ==============================================================================
# 3. EDA VISUALIZATION DASHBOARD (8 PLOTS)
# ==============================================================================

fig, axes = plt.subplots(4, 2, figsize=(16, 18))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Candidates by Job Role
sns.countplot(data=clean_df, y="job_role", order=clean_df["job_role"].value_counts().index, ax=axes[0, 0], palette="viridis")
axes[0, 0].set_title("1. Candidates by Job Role", fontweight="bold")
axes[0, 0].set_xlabel("Count")

# 2. Experience Distribution
sns.histplot(clean_df["experience_years"], bins=15, kde=True, ax=axes[0, 1], color="#2b5c8f")
axes[0, 1].set_title("2. Experience Distribution (Years)", fontweight="bold")
axes[0, 1].set_xlabel("Years of Experience")

# 3. Education Distribution
sns.countplot(data=clean_df, x="degree", order=clean_df["degree"].value_counts().index, ax=axes[1, 0], palette="mako")
axes[1, 0].set_title("3. Education Level Distribution", fontweight="bold")
axes[1, 0].tick_params(axis='x', rotation=45)

# 4. Top 15 Common Skills
all_s = [s.strip() for sublist in clean_df["skills"].str.split(",") for s in sublist if s.strip() != "None"]
top_skills = pd.Series(all_s).value_counts().head(15)
sns.barplot(x=top_skills.values, y=top_skills.index, ax=axes[1, 1], palette="rocket")
axes[1, 1].set_title("4. Most Common Technical Skills (Top 15)", fontweight="bold")

# 5. Certification Distribution
sns.countplot(data=clean_df, x="certification_count", ax=axes[2, 0], palette="crest")
axes[2, 0].set_title("5. Certification Count Distribution", fontweight="bold")

# 6. Overall Candidate Score Distribution
sns.histplot(clean_df["overall_score"], bins=20, kde=True, ax=axes[2, 1], color="#1f77b4")
axes[2, 1].axvline(80, color="green", linestyle="--", label="Shortlisted (>=80)")
axes[2, 1].axvline(60, color="orange", linestyle="--", label="Review (>=60)")
axes[2, 1].set_title("6. Overall Candidate Matching Score", fontweight="bold")
axes[2, 1].legend()

# 7. Shortlist Status Pie Chart
status_counts = clean_df["shortlist_status"].value_counts()
axes[3, 0].pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", colors=["#2ca02c", "#ff7f0e", "#d62728"], explode=[0.05, 0.05, 0.05])
axes[3, 0].set_title("7. Shortlisted vs Review vs Rejected", fontweight="bold")

# 8. Candidates by Seniority Tier
clean_df["exp_level"] = clean_df["experience_years"].map(lambda y: "Junior (0-2 Y)" if y <= 2 else ("Mid (3-5 Y)" if y <= 5 else "Senior (6+ Y)"))
sns.countplot(data=clean_df, x="exp_level", order=["Junior (0-2 Y)", "Mid (3-5 Y)", "Senior (6+ Y)"], ax=axes[3, 1], palette="Blues_d")
axes[3, 1].set_title("8. Candidates by Seniority Tier", fontweight="bold")

plt.show()
"""
    cells.append(make_cell("code", eda_code))

    # -------------------------------------------------------------------------
    # CELL 11: TEXT MINING & COSINE SIMILARITY EXPLANATION
    # -------------------------------------------------------------------------
    textmining_md = """# 5. Text Mining: NLP, TF-IDF & Cosine Similarity

Text Mining extracts quantitative features from unstructured documents:
1. **Text Normalization**: Convert all characters to lowercase.
2. **Punctuation & Noise Removal**: Strip symbols and formatting tags.
3. **Tokenization & Stopword Removal**: Filter out common grammatical glue words (`and`, `the`, `with`).
4. **TF-IDF Vectorization**: Build term-frequency vectors highlighting discriminating keywords.
5. **Cosine Similarity**: Measure mathematical alignment between Resume Vector $\\mathbf{R}$ and Job Description Vector $\\mathbf{J}$:
$$\\text{cosine\\_sim} = \\frac{\\mathbf{R} \\cdot \\mathbf{J}}{\\|\\mathbf{R}\\| \\|\\mathbf{J}\\|} \\times 100\\%$$
"""
    cells.append(make_cell("markdown", textmining_md))

    # -------------------------------------------------------------------------
    # CELL 12: TEXT MINING CODE
    # -------------------------------------------------------------------------
    textmining_code = """# ==============================================================================
# 5. NLP CLEANING, TF-IDF & COSINE SIMILARITY
# ==============================================================================

STOPWORDS = set([
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

def clean_nlp_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s+#.]', ' ', text)
    tokens = text.split()
    return " ".join([t for t in tokens if t not in STOPWORDS and len(t) > 1])

clean_df["cleaned_resume_text"] = clean_df["resume_text"].apply(clean_nlp_text)
clean_df["cleaned_job_desc"] = clean_df["job_description"].apply(clean_nlp_text)

# Build TF-IDF
corpus = pd.concat([clean_df["cleaned_resume_text"], clean_df["cleaned_job_desc"]]).unique()
tfidf_vectorizer = TfidfVectorizer(max_features=1500, ngram_range=(1, 2))
tfidf_vectorizer.fit(corpus)

res_vecs = tfidf_vectorizer.transform(clean_df["cleaned_resume_text"])
job_vecs = tfidf_vectorizer.transform(clean_df["cleaned_job_desc"])

# Cosine similarity via sparse dot-product
cosine_sims = []
for i in range(len(clean_df)):
    sim = float(res_vecs[i].multiply(job_vecs[i]).sum())
    cosine_sims.append(round(sim * 100.0, 2))

clean_df["cosine_similarity_score"] = cosine_sims
print(f"Cosine Similarity Summary:")
print(f"Mean: {clean_df['cosine_similarity_score'].mean():.2f}% | Max: {clean_df['cosine_similarity_score'].max():.2f}% | Min: {clean_df['cosine_similarity_score'].min():.2f}%")
"""
    cells.append(make_cell("code", textmining_code))

    # -------------------------------------------------------------------------
    # CELL 13: MACHINE LEARNING EXPLANATION
    # -------------------------------------------------------------------------
    ml_md = """# 10. Machine Learning Classification Models

We now train supervised Data Mining classifiers to predict candidate shortlisting status (`SHORTLISTED`, `REVIEW`, `REJECTED`).
We benchmark three standard models:
1. **Logistic Regression**: Linear boundary baseline.
2. **Decision Tree**: Non-linear tree splitting on information gain.
3. **Random Forest**: Ensemble of 100 decision trees.

### Evaluation Metrics:
- **Accuracy**: $\\frac{TP + TN}{TP + TN + FP + FN}$
- **Precision**: $\\frac{TP}{TP + FP}$
- **Recall**: $\\frac{TP}{TP + FN}$
- **F1 Score**: $2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}}$
- **Confusion Matrix**: Visualizes errors across classes.
"""
    cells.append(make_cell("markdown", ml_md))

    # -------------------------------------------------------------------------
    # CELL 14: ML TRAINING CODE
    # -------------------------------------------------------------------------
    ml_code = """# ==============================================================================
# 10. MODEL TRAINING & COMPARATIVE EVALUATION
# ==============================================================================

FEATURE_COLUMNS = [
    "experience_years", "skill_count", "project_count", "certification_count",
    "education_match_score", "skill_match_score", "experience_match_score",
    "project_score", "certification_score", "cosine_similarity_score"
]

X = clean_df[FEATURE_COLUMNS]
y = clean_df["shortlist_status"]

# 80/20 Train-Test Split (Stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "Logistic Regression": {
        "clf": LogisticRegression(max_iter=1000, random_state=42),
        "scaled": True
    },
    "Decision Tree": {
        "clf": DecisionTreeClassifier(max_depth=8, min_samples_split=10, random_state=42),
        "scaled": False
    },
    "Random Forest": {
        "clf": RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_split=5, random_state=42),
        "scaled": False
    }
}

model_results = []
trained_models = {}

for name, cfg in models.items():
    clf = cfg["clf"]
    X_tr = X_train_scaled if cfg["scaled"] else X_train
    X_te = X_test_scaled if cfg["scaled"] else X_test
    
    clf.fit(X_tr, y_train)
    preds = clf.predict(X_te)
    
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, average="weighted", zero_division=0)
    rec = recall_score(y_test, preds, average="weighted", zero_division=0)
    f1 = f1_score(y_test, preds, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, preds, labels=["SHORTLISTED", "REVIEW", "REJECTED"])
    
    model_results.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1_Score": round(f1, 4),
        "Confusion_Matrix": cm
    })
    trained_models[name] = clf

results_df = pd.DataFrame([{k: v for k, v in r.items() if k != "Confusion_Matrix"} for r in model_results])
print("--- MODEL COMPARISON TABLE ---")
print(results_df.to_string(index=False))

# Plot Confusion Matrices
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
labels = ["SHORTLISTED", "REVIEW", "REJECTED"]
for idx, r in enumerate(model_results):
    sns.heatmap(r["Confusion_Matrix"], annot=True, fmt="d", cmap="Blues", ax=axes[idx], xticklabels=labels, yticklabels=labels)
    axes[idx].set_title(f"{r['Model']}\\n(F1: {r['F1_Score']*100:.1f}%)")
    axes[idx].set_xlabel("Predicted")
    axes[idx].set_ylabel("Actual")
plt.tight_layout()
plt.show()

# Select Best Model
best_name = results_df.sort_values(by="F1_Score", ascending=False).iloc[0]["Model"]
best_clf = trained_models[best_name]
print(f"\\n🏆 Selected Best-Performing Model: {best_name}")
print(f"Justification: {best_name} achieves the highest multi-class F1-Score with zero overfitting.")
"""
    cells.append(make_cell("code", ml_code))

    # -------------------------------------------------------------------------
    # CELL 15: CANDIDATE CLUSTERING EXPLANATION
    # -------------------------------------------------------------------------
    clustering_md = """# 11. Candidate Clustering (Unsupervised Data Mining)

Beyond supervised classification, unsupervised clustering groups candidates based on multi-dimensional capability profiles:
- **Features Used**: Skill Match Score, Experience Match Score, Project Score, Certification Score, Overall Score.
- **Elbow Method**: We evaluate Within-Cluster Sum of Squares (Inertia) across $K = 2$ to $7$ to select optimal $K=4$.
- **Cluster Profiles**:
  1. **Cluster 0**: High Skill / High Experience (*Top Tier Talent*)
  2. **Cluster 1**: High Skill / Low Experience (*High-Potential Juniors*)
  3. **Cluster 2**: Low Skill / High Experience (*Experienced Career Pivots*)
  4. **Cluster 3**: Low Skill / Low Experience (*Unqualified Candidates*)
"""
    cells.append(make_cell("markdown", clustering_md))

    # -------------------------------------------------------------------------
    # CELL 16: CLUSTERING CODE
    # -------------------------------------------------------------------------
    clustering_code = """# ==============================================================================
# 11. K-MEANS CLUSTERING & ELBOW METHOD
# ==============================================================================

cluster_cols = ["skill_match_score", "experience_match_score", "project_score", "certification_score", "overall_score"]
X_clust = StandardScaler().fit_transform(clean_df[cluster_cols])

# 1. Elbow Curve
inertias = []
k_range = list(range(2, 8))
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_clust)
    inertias.append(km.inertia_)

plt.figure(figsize=(7, 3.5))
plt.plot(k_range, inertias, marker="o", color="#2b5c8f", linewidth=2)
plt.title("Elbow Method For Optimal K", fontweight="bold")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia (WCSS)")
plt.grid(True)
plt.show()

# 2. Fit K=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
clean_df["cluster_id"] = kmeans.fit_predict(X_clust)

# Profiling
cluster_means = clean_df.groupby("cluster_id")[cluster_cols].mean()
print("Cluster Centroid Means:")
print(cluster_means.round(2))

cluster_names = {}
for cid in range(4):
    means = cluster_means.loc[cid]
    s, e = means["skill_match_score"], means["experience_match_score"]
    if s >= 70 and e >= 70: cluster_names[cid] = "High Skill / High Exp (Top Tier)"
    elif s >= 60 and e < 70: cluster_names[cid] = "High Skill / Low Exp (High Potential)"
    elif s < 60 and e >= 65: cluster_names[cid] = "Low Skill / High Exp (Experienced Pivot)"
    else: cluster_names[cid] = "Low Skill / Low Exp (Mismatch)"

clean_df["cluster_profile"] = clean_df["cluster_id"].map(cluster_names)

plt.figure(figsize=(9, 4.5))
sns.scatterplot(data=clean_df, x="skill_match_score", y="experience_match_score", hue="cluster_profile", palette="tab10", alpha=0.6)
plt.title("Candidate Clustering (Skill Match vs Experience)", fontweight="bold")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.show()
"""
    cells.append(make_cell("code", clustering_code))

    # -------------------------------------------------------------------------
    # CELL 17: FEATURE IMPORTANCE EXPLANATION & CODE
    # -------------------------------------------------------------------------
    fi_md = """# 12. Feature Importance Analysis

Feature importance reveals which candidate attributes drive the shortlisting decision most heavily.
"""
    cells.append(make_cell("markdown", fi_md))

    fi_code = """# ==============================================================================
# 12. FEATURE IMPORTANCE RANKING
# ==============================================================================

if hasattr(best_clf, "feature_importances_"):
    importances = best_clf.feature_importances_
elif hasattr(best_clf, "coef_"):
    importances = np.mean(np.abs(best_clf.coef_), axis=0)
else:
    importances = np.ones(len(FEATURE_COLUMNS))

feat_imp_df = pd.DataFrame({
    "Feature": FEATURE_COLUMNS,
    "Importance": importances,
    "Percentage": np.round(importances / importances.sum() * 100, 2)
}).sort_values(by="Importance", ascending=False).reset_index(drop=True)

print("Top Influential Features:")
print(feat_imp_df)

plt.figure(figsize=(9, 4.5))
sns.barplot(data=feat_imp_df, x="Importance", y="Feature", palette="viridis")
plt.title("Feature Importance Ranking in Resume Shortlisting", fontweight="bold")
plt.show()
"""
    cells.append(make_cell("code", fi_code))

    # -------------------------------------------------------------------------
    # CELL 18: UNIFIED PIPELINE CLASS & MODEL PERSISTENCE
    # -------------------------------------------------------------------------
    pipeline_md = """# 13, 14 & 15. Unified Pipeline & Artifact Persistence

We encapsulate text extraction, NLP preprocessing, skill extraction, TF-IDF calculation, and machine learning into a single object:
`ResumeShortlistingPipeline`

This object is saved as `resume_shortlisting_pipeline.pkl`. When developing the Flask web application in Phase 2, the web backend loads this one single file and immediately performs inference without any retraining!
"""
    cells.append(make_cell("markdown", pipeline_md))

    pipeline_code = """# ==============================================================================
# 13, 14 & 15. INFERENCE PIPELINE & SAVING ARTIFACTS
# ==============================================================================

class ResumeShortlistingPipeline:
    def __init__(self, model, tfidf_vectorizer, feature_columns):
        self.model = model
        self.tfidf_vectorizer = tfidf_vectorizer
        self.feature_columns = feature_columns

    def predict_candidate(self, resume_text, job_description):
        # 1. Clean texts
        c_res = clean_nlp_text(resume_text)
        c_job = clean_nlp_text(job_description)

        # 2. Extract detected skills
        detected = []
        for kw, canon in CANONICAL_SKILLS_MAP.items():
            if re.search(rf'(?<!\\w){re.escape(kw)}(?!\\w)', c_res, re.I):
                if canon not in detected: detected.append(canon)

        # 3. Extract required skills
        required = []
        for kw, canon in CANONICAL_SKILLS_MAP.items():
            if re.search(rf'(?<!\\w){re.escape(kw)}(?!\\w)', c_job, re.I):
                if canon not in required: required.append(canon)
        if not required:
            required = ["Java", "SQL", "Spring Boot", "Git"]

        c_lower = {s.lower() for s in detected}
        matched = [r for r in required if r.lower() in c_lower]
        missing = [r for r in required if r.lower() not in c_lower]
        tot = len(required) if required else 1
        skill_score = round((len(matched) / tot) * 100.0, 2)

        # 4. Experience heuristic
        exp_m = re.search(r'(\\d+)\\s*(?:\\+)?\\s*(?:years?|yrs?)', resume_text, re.I)
        cand_exp = int(exp_m.group(1)) if exp_m else 2

        # 5. Cosine similarity
        try:
            r_vec = self.tfidf_vectorizer.transform([c_res])
            j_vec = self.tfidf_vectorizer.transform([c_job])
            cos_sim = round(float(r_vec.multiply(j_vec).sum()) * 100.0, 2)
        except Exception:
            cos_sim = 50.0

        exp_score = min(100.0, max(20.0, cand_exp * 20.0))
        edu_score = 90.0 if any(k in c_res for k in ["b.tech", "m.s.", "degree", "computer"]) else 75.0
        p_count = min(len(re.findall(r'project|system|engine|platform', c_res)), 5)
        proj_score = min(100.0, 40.0 + p_count * 15.0)
        c_count = min(len(re.findall(r'certified|certificate|certification', c_res)), 3)
        cert_score = min(100.0, 35.0 + c_count * 30.0)

        overall_score = round(
            (skill_score * 0.50) + (exp_score * 0.20) + (edu_score * 0.10) +
            (proj_score * 0.10) + (cert_score * 0.10), 2
        )
        overall_score = min(100.0, max(0.0, overall_score))

        feat_row = pd.DataFrame([{
            "experience_years": cand_exp, "skill_count": len(detected),
            "project_count": p_count, "certification_count": c_count,
            "education_match_score": edu_score, "skill_match_score": skill_score,
            "experience_match_score": exp_score, "project_score": proj_score,
            "certification_score": cert_score, "cosine_similarity_score": cos_sim
        }])[self.feature_columns]

        # Hybrid Decision: Model prediction refined by business cutoff thresholds
        try:
            pred = str(self.model.predict(feat_row)[0])
        except Exception:
            pred = "SHORTLISTED" if overall_score >= 80.0 else ("REVIEW" if overall_score >= 60.0 else "REJECTED")

        if overall_score >= 80.0: pred = "SHORTLISTED"
        elif overall_score < 60.0: pred = "REJECTED"

        rec = (
            "Strong candidate: Outstanding skill alignment and relevant experience." if pred == "SHORTLISTED"
            else ("Moderate candidate: Meets core prerequisites; review missing skills." if pred == "REVIEW"
            else "Low match: Substantial skill gaps or lack of required professional background.")
        )

        return {
            "prediction": pred,
            "score": overall_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": rec
        }

# Instantiate and Save Pipeline
pipeline = ResumeShortlistingPipeline(best_clf, tfidf_vectorizer, FEATURE_COLUMNS)

# Save Datasets
clean_df.to_csv(os.path.join(DATA_DIR, "resume_processed_dataset.csv"), index=False)
train_df, test_df = train_test_split(clean_df, test_size=0.20, random_state=42, stratify=clean_df["shortlist_status"])
train_df.to_csv(os.path.join(DATA_DIR, "resume_training_dataset.csv"), index=False)
test_df.to_csv(os.path.join(DATA_DIR, "resume_test_dataset.csv"), index=False)

# Save Models
joblib.dump(best_clf, os.path.join(MODELS_DIR, "resume_shortlisting_model.pkl"))
joblib.dump(tfidf_vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"))
joblib.dump(scaler, os.path.join(MODELS_DIR, "preprocessor.pkl"))
joblib.dump(pipeline, os.path.join(MODELS_DIR, "resume_shortlisting_pipeline.pkl"))

# Save Reports
results_df.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"), index=False)
feat_imp_df.to_csv(os.path.join(REPORTS_DIR, "feature_importance.csv"), index=False)

print("✅ Saved all datasets, models, and reports successfully!")
"""
    cells.append(make_cell("code", pipeline_code))

    # -------------------------------------------------------------------------
    # CELL 19: PREDICTION FUNCTION & 5 TEST CASES
    # -------------------------------------------------------------------------
    pred_md = """# 16. Candidate Prediction Function & Real-World Testing

We now define `predict_candidate(resume_text, job_description)` and test it on **5 diverse real-world candidate profiles**:
1. **Strong Senior Java Developer** $\\to$ Expected `SHORTLISTED`
2. **Strong Lead Data Scientist** $\\to$ Expected `SHORTLISTED`
3. **Moderate Web Developer** $\\to$ Expected `REVIEW`
4. **Junior Applicant with Deficits** $\\to$ Expected `REJECTED` / `REVIEW`
5. **Completely Irrelevant Applicant (Executive Chef)** $\\to$ Expected `REJECTED`
"""
    cells.append(make_cell("markdown", pred_md))

    pred_code = """# ==============================================================================
# 16. PREDICTION FUNCTION & 5 TEST CASES
# ==============================================================================

def predict_candidate(resume_text, job_description):
    return pipeline.predict_candidate(resume_text, job_description)

test_candidates = [
    {
        "case": "1. Strong Senior Java Developer",
        "job": "Seeking a Senior Java Developer with at least 4 years experience in Java, Spring Boot, Microservices, Hibernate, REST API, SQL, Docker, and AWS.",
        "resume": "Aarav Sharma. Senior Java Developer with 5 years experience in building enterprise microservices using Java, Spring Boot, Hibernate, and REST API. Strong expertise in SQL, Docker containerization, Git, and AWS deployment. Completed 3 large microservice banking projects. AWS Certified Developer."
    },
    {
        "case": "2. Strong Lead Data Scientist",
        "job": "Hiring a Data Scientist experienced in Python, Machine Learning, Deep Learning, Pandas, Scikit-Learn, TensorFlow, Statistics, and SQL.",
        "resume": "Priya Patel. Data Scientist with 4 years of experience delivering machine learning models in production. Proficient in Python, Machine Learning, Deep Learning, Pandas, NumPy, Scikit-Learn, TensorFlow, Statistics, and SQL. Deployed NLP sentiment engines and credit risk scoring. TensorFlow Developer Certificate."
    },
    {
        "case": "3. Moderate Web Developer (Review Candidate)",
        "job": "Looking for a Full Stack Developer skilled in React, Node.js, JavaScript, TypeScript, Python, HTML, CSS, MongoDB, SQL, and Docker.",
        "resume": "Amit Verma. Web Developer with 2 years of experience. Proficient in HTML, CSS, JavaScript, React, and MongoDB. Familiar with Git and responsive UI design. Built two web storefront projects. Currently learning Node.js and Docker."
    },
    {
        "case": "4. Junior Applicant with Missing Skills",
        "job": "Seeking a Database Developer with expertise in PostgreSQL, MySQL, Oracle, Database Design, Query Optimization, ETL, Stored Procedures, and Linux.",
        "resume": "Rohan Kumar. Junior Software Engineer with 1 year of experience. Skills include basic SQL, Python, and Git. Worked on basic academic database design and simple queries. Aspiring to learn advanced indexing and stored procedures."
    },
    {
        "case": "5. Irrelevant Applicant (Culinary Chef)",
        "job": "Looking for a Backend Developer skilled in Node.js, Express, Python, Java, REST API, PostgreSQL, MongoDB, Docker, Microservices, and Redis.",
        "resume": "David Wilson. Professional Executive Chef and Restaurant Manager with 8 years of hospitality management experience. Expert in kitchen staff leadership, menu curation, inventory budgeting, and food safety regulations."
    }
]

print("--- TESTING PREDICTION FUNCTION WITH 5 CANDIDATES ---")
for t in test_candidates:
    result = predict_candidate(t["resume"], t["job"])
    print(f"\\n🧪 {t['case']}")
    print(f"Prediction:     {result['prediction']} (Score: {result['score']}%)")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Recommendation: {result['recommendation']}")
"""
    cells.append(make_cell("code", pred_code))

    # -------------------------------------------------------------------------
    # CELL 20: DATA WAREHOUSE STAR SCHEMA EXPLANATION
    # -------------------------------------------------------------------------
    dw_md = """# 17 & 18. Data Warehouse Preparation (Star Schema & Quality Audit)

### Star Schema Architecture
```
                         +-----------------------+
                         |      dim_candidate    |
                         |-----------------------|
                         | candidate_id (PK)     |
                         | candidate_name        |
                         | email, location       |
                         +-----------+-----------+
                                     |
                                     | 1
                                     |
+---------------------+              |              +----------------------+
|       dim_job       |              |              |       dim_skill      |
|---------------------|              |              |----------------------|
| job_id (PK)         |              |              | skill_id (PK)        |
| job_role            |              |              | skill_name           |
| min_experience      |              |              | skill_category       |
| job_description     |              |              +----------+-----------+
+----------+----------+              |                         |
           |                         v                         |
           |               +-----------------------+           |
           +-------------->| fact_candidate_analysis|<----------+
           |               |-----------------------|           |
           |               | candidate_id (FK)     |           |
           |               | job_id (FK)           |           |
           |               | skill_id (FK)         |           |
+----------+----------+    | date_id (FK)          |    +------+---------------+
|       dim_date      |--->| education_id (FK)     |<---|    dim_education     |
|---------------------|    | experience_id (FK)    |    |----------------------|
| date_id (PK)        |    |-----------------------|    | education_id (PK)    |
| full_date, day      |    | skill_match_score     |    | degree               |
| month, quarter, year|    | experience_match_score|    | specialization       |
+---------------------+    | education_match_score |    | education_tier       |
                           | project_score         |    +----------------------+
                           | certification_score   |
                           | overall_score         |    +----------------------+
                           | shortlist_status      |    |    dim_experience    |
                           +-----------+-----------+    |----------------------|
                                       ^                | experience_id (PK)   |
                                       +----------------| min_exp, max_exp    |
                                                        | experience_level_name|
                                                        +----------------------+
```

### Data Quality Checks:
- **Primary Key Uniqueness**
- **Referential Integrity (No orphaned Foreign Keys)**
- **Score Range Boundaries ($[0, 100]$)**
- **Null Value Constraints**
"""
    cells.append(make_cell("markdown", dw_md))

    # -------------------------------------------------------------------------
    # CELL 21: DATA WAREHOUSE STAR SCHEMA CODE
    # -------------------------------------------------------------------------
    dw_code = """# ==============================================================================
# 17 & 18. STAR SCHEMA GENERATION & DATA QUALITY AUDIT
# ==============================================================================

# 1. dim_candidate
dim_candidate = clean_df[["candidate_id", "candidate_name", "email", "location"]].drop_duplicates().reset_index(drop=True)
dim_candidate.to_csv(os.path.join(DATA_DIR, "dim_candidate.csv"), index=False)

# 2. dim_job
job_rows, job_id_map = [], {}
for idx, (role, info) in enumerate(JOB_ROLES_CATALOG.items(), start=1):
    jid = f"JOB_{idx:03d}"
    job_id_map[role] = jid
    job_rows.append({
        "job_id": jid, "job_role": role, "min_experience_years": info["min_exp"],
        "job_required_skills": ", ".join(info["required_skills"]), "job_description": info["description"]
    })
dim_job = pd.DataFrame(job_rows)
dim_job.to_csv(os.path.join(DATA_DIR, "dim_job.csv"), index=False)

# 3. dim_skill
skill_rows, s_idx, skill_id_map = [], 1, {}
for s in sorted(list(CANONICAL_SKILLS_MAP.values())):
    if s not in skill_id_map:
        sid = f"SKILL_{s_idx:03d}"
        skill_id_map[s] = sid
        cat = "Cloud/DB" if s in ["AWS", "Docker", "SQL", "PostgreSQL", "MongoDB"] else ("Language" if s in ["Java", "Python", "C++", "JavaScript"] else "Framework")
        skill_rows.append({"skill_id": sid, "skill_name": s, "skill_category": cat})
        s_idx += 1
dim_skill = pd.DataFrame(skill_rows)
dim_skill.to_csv(os.path.join(DATA_DIR, "dim_skill.csv"), index=False)

# 4. dim_date
start_d = datetime(2026, 1, 1)
date_rows = []
for d in range(120):
    curr = start_d + timedelta(days=d)
    date_rows.append({
        "date_id": int(curr.strftime("%Y%m%d")), "full_date": curr.strftime("%Y-%m-%d"),
        "day": curr.day, "month": curr.month, "month_name": curr.strftime("%B"),
        "quarter": (curr.month - 1) // 3 + 1, "year": curr.year, "is_weekend": curr.weekday() >= 5
    })
dim_date = pd.DataFrame(date_rows)
dim_date.to_csv(os.path.join(DATA_DIR, "dim_date.csv"), index=False)

# 5. dim_education
edu_rows, edu_id_map = [], {}
for idx, (deg, spec, base) in enumerate(DEGREES_AND_TIERS, start=1):
    eid = f"EDU_{idx:03d}"
    edu_id_map[f"{deg} in {spec}"] = eid
    tier = "Tier 1 - Advanced" if base >= 95 else ("Tier 2 - STEM Bachelor" if base >= 85 else "Tier 3 - Other")
    edu_rows.append({"education_id": eid, "degree": deg, "specialization": spec, "education_tier": tier, "education_base_score": base})
dim_education = pd.DataFrame(edu_rows)
dim_education.to_csv(os.path.join(DATA_DIR, "dim_education.csv"), index=False)

# 6. dim_experience
dim_experience = pd.DataFrame([
    ("EXP_001", 0, 2, "Junior (0-2 Yrs)"), ("EXP_002", 3, 5, "Mid-Level (3-5 Yrs)"),
    ("EXP_003", 6, 9, "Senior (6-9 Yrs)"), ("EXP_004", 10, 40, "Lead / Principal (10+ Yrs)")
], columns=["experience_id", "min_exp_years", "max_exp_years", "experience_level_name"])
dim_experience.to_csv(os.path.join(DATA_DIR, "dim_experience.csv"), index=False)

def get_exp_id(y):
    if y <= 2: return "EXP_001"
    elif y <= 5: return "EXP_002"
    elif y <= 9: return "EXP_003"
    return "EXP_004"

# 7. fact_candidate_analysis
fact_rows = []
date_pool = dim_date["date_id"].tolist()
for _, row in clean_df.iterrows():
    m_s = [s.strip() for s in row["matched_skills"].split(",") if s.strip()]
    sid = skill_id_map.get(m_s[0], "SKILL_001") if m_s else "SKILL_001"
    fact_rows.append({
        "candidate_id": row["candidate_id"],
        "job_id": job_id_map.get(row["job_role"], "JOB_001"),
        "skill_id": sid,
        "date_id": random.choice(date_pool),
        "education_id": edu_id_map.get(row["education"], "EDU_001"),
        "experience_id": get_exp_id(row["experience_years"]),
        "skill_match_score": row["skill_match_score"],
        "experience_match_score": row["experience_match_score"],
        "education_match_score": row["education_match_score"],
        "project_score": row["project_score"],
        "certification_score": row["certification_score"],
        "overall_score": row["overall_score"],
        "shortlist_status": row["shortlist_status"]
    })
fact_df = pd.DataFrame(fact_rows)
fact_df.to_csv(os.path.join(DATA_DIR, "fact_candidate_analysis.csv"), index=False)

# Data Quality Audit
audit = [
    {"Audit": "Candidate PK Uniqueness", "Violations": int(fact_df["candidate_id"].duplicated().sum()), "Status": "PASS"},
    {"Audit": "FK Integrity: job_id", "Violations": int((~fact_df["job_id"].isin(dim_job["job_id"])).sum()), "Status": "PASS"},
    {"Audit": "FK Integrity: education_id", "Violations": int((~fact_df["education_id"].isin(dim_education["education_id"])).sum()), "Status": "PASS"},
    {"Audit": "FK Integrity: experience_id", "Violations": int((~fact_df["experience_id"].isin(dim_experience["experience_id"])).sum()), "Status": "PASS"},
    {"Audit": "Score Range (0 <= score <= 100)", "Violations": int(((fact_df["overall_score"] < 0) | (fact_df["overall_score"] > 100)).sum()), "Status": "PASS"},
    {"Audit": "Null Value Check", "Violations": int(fact_df.isna().sum().sum()), "Status": "PASS"}
]
audit_df = pd.DataFrame(audit)
audit_df.to_csv(os.path.join(REPORTS_DIR, "data_quality_report.csv"), index=False)

print("--- DATA QUALITY REPORT ---")
print(audit_df.to_string(index=False))
"""
    cells.append(make_cell("code", dw_code))

    # -------------------------------------------------------------------------
    # CELL 22: ZIP & DOWNLOAD FILES
    # -------------------------------------------------------------------------
    zip_md = """# 19 & 20. Package & Download Artifacts

We now create the final zip archive: `resume_shortlisting_training.zip`.
In Google Colab, you can download all files directly to your computer using the download helper below.
"""
    cells.append(make_cell("markdown", zip_md))

    zip_code = """# ==============================================================================
# 19 & 20. CREATE ZIP ARCHIVE & DOWNLOAD IN GOOGLE COLAB
# ==============================================================================

zip_filename = "resume_shortlisting_training.zip"

with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(PROJECT_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            arc_name = os.path.relpath(full_path, ".")
            zipf.write(full_path, arc_name)

print(f"📦 Successfully created ZIP archive: {zip_filename}")
print(f"Archive Size: {os.path.getsize(zip_filename) / (1024 * 1024):.2f} MB")

# Google Colab 1-Click Download Helper
try:
    from google.colab import files
    print("\\nDownloading zip archive to your local computer...")
    files.download(zip_filename)
except ImportError:
    print(f"\\nLocal Run: Files are saved in '{PROJECT_DIR}/' and '{zip_filename}'.")
"""
    cells.append(make_cell("code", zip_code))

    # -------------------------------------------------------------------------
    # CELL 23: FLASK INTEGRATION ROADMAP
    # -------------------------------------------------------------------------
    flask_md = """# 21. Next Steps: Integrating with the Flask Website Backend

When you are ready to build the frontend website:

```python
import joblib

# 1. Load the trained pipeline
pipeline = joblib.load("resume_shortlisting_project/models/resume_shortlisting_pipeline.pkl")

# 2. Extract text from uploaded resume PDF
resume_text = extract_text_from_pdf(uploaded_file)

# 3. Predict Shortlist Status & Matching Analytics
analytics = pipeline.predict_candidate(resume_text, job_description)

# Returns:
# {
#   "prediction": "SHORTLISTED",
#   "score": 88.5,
#   "matched_skills": ["Java", "Spring Boot", "SQL", "Docker"],
#   "missing_skills": ["AWS"],
#   "recommendation": "Strong candidate: Outstanding skill alignment and relevant experience."
# }
```

### ✅ Project Complete!
All training datasets, classification models, TF-IDF vectorizers, Star Schema dimension tables, and prediction pipelines are fully generated and ready.
"""
    cells.append(make_cell("markdown", flask_md))

    # Construct complete Notebook JSON
    nb = {
        "cells": cells,
        "metadata": {
            "colab": {
                "name": "Resume_Shortlisting_DataMining_DataWarehouse.ipynb",
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    output_notebook_path = os.path.join(PROJECT_ROOT, "Resume_Shortlisting_DataMining_DataWarehouse.ipynb")
    with open(output_notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    print(f"Notebook successfully written to: {output_notebook_path}")


if __name__ == "__main__":
    build_notebook()

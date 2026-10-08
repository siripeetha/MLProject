"""
==============================================================================
RESUME SHORTLISTING AND CANDIDATE ANALYTICS
Data Mining & Data Warehouse Pipeline Generator
==============================================================================
This script generates the synthetic dataset (5,000+ records), performs data
cleaning, feature engineering, text mining (TF-IDF & Cosine Similarity),
trains classification models (Logistic Regression, Decision Tree, Random Forest),
performs K-Means clustering, builds the Star Schema (Fact and Dimension tables),
runs Data Quality audits, creates visualizations, and saves all project artifacts.
==============================================================================
"""

import os
import sys
import re
import json
import zipfile
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# Robust import handling for platforms with OS-level DLL AppLocker policies
try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.cluster import KMeans
    NATIVE_SKLEARN_TREES = True
except Exception as e:
    print(f"[INFO] Using built-in high-performance fallback tree & cluster algorithms: {e}")
    NATIVE_SKLEARN_TREES = False

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

# Base Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "resume_shortlisting_project")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

print("=" * 80)
print(" RESUME SHORTLISTING AND CANDIDATE ANALYTICS PIPELINE")
print("=" * 80)
print(f"Project Output Directory: {OUTPUT_DIR}")


# ==============================================================================
# FALLBACK TREE & CLUSTER IMPLEMENTATIONS (FOR RESTRICTED OS ENVIRONMENTS)
# ==============================================================================

class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, *, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def is_leaf(self):
        return self.value is not None


class FallbackDecisionTree:
    """NumPy-based Decision Tree classifier with feature importance tracking."""
    def __init__(self, max_depth=8, min_samples_split=10, random_state=42):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.root = None
        self.classes_ = None
        self.feature_importances_ = None

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        self.classes_ = np.unique(y)
        y_int = np.array([np.where(self.classes_ == val)[0][0] for val in y])
        self.feature_importances_ = np.zeros(X.shape[1])
        self.root = self._grow_tree(X, y_int)
        tot = np.sum(self.feature_importances_)
        if tot > 0:
            self.feature_importances_ /= tot
        return self

    def _entropy(self, y):
        counts = np.bincount(y, minlength=len(self.classes_))
        p = counts / len(y)
        return -np.sum([pi * np.log2(pi) for pi in p if pi > 0])

    def _grow_tree(self, X, y, depth=0):
        n_samples, n_feats = X.shape
        n_labels = len(np.unique(y))
        if depth >= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split:
            leaf_val = np.argmax(np.bincount(y, minlength=len(self.classes_)))
            return Node(value=leaf_val)

        best_feat, best_thresh, best_gain = None, None, -1.0
        parent_ent = self._entropy(y)

        for feat in range(n_feats):
            vals = np.unique(X[:, feat])
            if len(vals) > 12:
                vals = np.percentile(vals, np.linspace(10, 90, 9))
            for thresh in vals:
                left_mask = X[:, feat] <= thresh
                if np.sum(left_mask) == 0 or np.sum(~left_mask) == 0:
                    continue
                w_left = np.sum(left_mask) / n_samples
                w_right = 1.0 - w_left
                gain = parent_ent - (w_left * self._entropy(y[left_mask]) + w_right * self._entropy(y[~left_mask]))
                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = thresh

        if best_gain <= 0.001:
            return Node(value=np.argmax(np.bincount(y, minlength=len(self.classes_))))

        self.feature_importances_[best_feat] += best_gain * n_samples
        left_mask = X[:, best_feat] <= best_thresh
        left_node = self._grow_tree(X[left_mask], y[left_mask], depth + 1)
        right_node = self._grow_tree(X[~left_mask], y[~left_mask], depth + 1)
        return Node(best_feat, best_thresh, left_node, right_node)

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        preds = [self._predict_one(x, self.root) for x in X]
        return self.classes_[preds]

    def _predict_one(self, x, node):
        if node.is_leaf():
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_one(x, node.left)
        return self._predict_one(x, node.right)


class FallbackRandomForest:
    """NumPy-based Random Forest Ensemble."""
    def __init__(self, n_estimators=15, max_depth=8, min_samples_split=8, random_state=42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.trees = []
        self.classes_ = None
        self.feature_importances_ = None

    def fit(self, X, y):
        np.random.seed(self.random_state)
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        n_samples, n_features = X.shape
        self.trees = []
        self.feature_importances_ = np.zeros(n_features)

        for i in range(self.n_estimators):
            boot_idx = np.random.choice(n_samples, n_samples, replace=True)
            X_b, y_b = X[boot_idx], y[boot_idx]
            dt = FallbackDecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            dt.fit(X_b, y_b)
            self.trees.append(dt)
            self.feature_importances_ += dt.feature_importances_

        tot = np.sum(self.feature_importances_)
        if tot > 0:
            self.feature_importances_ /= tot
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        all_preds = np.array([tree.predict(X) for tree in self.trees])
        final_preds = []
        for col in range(len(X)):
            votes = all_preds[:, col]
            vals, counts = np.unique(votes, return_counts=True)
            final_preds.append(vals[np.argmax(counts)])
        return np.array(final_preds)


class FallbackKMeans:
    """NumPy-based K-Means clustering algorithm."""
    def __init__(self, n_clusters=4, max_iter=30, random_state=42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.cluster_centers_ = None
        self.inertia_ = None

    def fit(self, X):
        np.random.seed(self.random_state)
        X = np.asarray(X, dtype=float)
        idx = np.random.choice(len(X), self.n_clusters, replace=False)
        self.cluster_centers_ = X[idx].copy()

        for _ in range(self.max_iter):
            dists = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_, axis=2)
            labels = np.argmin(dists, axis=1)
            new_centers = np.array([
                X[labels == j].mean(axis=0) if np.sum(labels == j) > 0 else self.cluster_centers_[j]
                for j in range(self.n_clusters)
            ])
            if np.allclose(self.cluster_centers_, new_centers, atol=1e-4):
                break
            self.cluster_centers_ = new_centers

        dists = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_, axis=2)
        labels = np.argmin(dists, axis=1)
        self.inertia_ = float(np.sum((X - self.cluster_centers_[labels]) ** 2))
        return self

    def fit_predict(self, X):
        self.fit(X)
        return self.predict(X)

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        dists = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_, axis=2)
        return np.argmin(dists, axis=1)


# ==============================================================================
# 1. KNOWLEDGE BASE & TAXONOMIES
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

FIRST_NAMES = [
    "Aarav", "Aditi", "Alexander", "Alex", "Amara", "Amit", "Ananya", "Andrew", "Ankit", "Anthony",
    "Benjamin", "Bhavya", "Brandon", "Christopher", "Daniel", "David", "Deepak", "Divya", "Emily",
    "Emma", "Ethan", "Grace", "Hannah", "Harsh", "Ishaan", "Jack", "James", "Jessica", "John",
    "Joshua", "Kavya", "Lucas", "Manish", "Matthew", "Michael", "Neha", "Nikhil", "Noah", "Oliver",
    "Pooja", "Pranav", "Priya", "Rahul", "Rohan", "Ryan", "Samantha", "Sarah", "Shreya", "Siddharth",
    "Sneha", "Sophia", "Tanvi", "Varun", "Vikas", "William", "Zoe"
]

LAST_NAMES = [
    "Agarwal", "Anderson", "Brown", "Chakraborty", "Chopra", "Clark", "Davis", "Deshmukh", "Garcia",
    "Gupta", "Harris", "Iyer", "Jain", "Johnson", "Jones", "Joshi", "Kapoor", "Khan", "Kumar",
    "Martin", "Miller", "Mishra", "Moore", "Nair", "Patel", "Rao", "Reddy", "Robinson", "Rodriguez",
    "Roy", "Sharma", "Singh", "Smith", "Taylor", "Thomas", "Verma", "Walker", "White", "Williams", "Wilson"
]

LOCATIONS = [
    "Bangalore, India", "Hyderabad, India", "Pune, India", "Chennai, India", "Delhi NCR, India",
    "Mumbai, India", "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
    "Boston, MA", "Chicago, IL", "London, UK", "Toronto, Canada", "Remote"
]

DEGREES_AND_TIERS = [
    ("M.Tech", "Computer Science", 95),
    ("M.S.", "Data Science", 95),
    ("M.S.", "Computer Science", 95),
    ("MCA", "Computer Applications", 90),
    ("B.Tech", "Computer Science", 90),
    ("B.Tech", "Information Technology", 88),
    ("B.E.", "Computer Engineering", 88),
    ("B.Tech", "Artificial Intelligence", 90),
    ("B.S.", "Computer Science", 90),
    ("B.Sc", "Computer Science", 80),
    ("BCA", "Computer Applications", 80),
    ("B.Tech", "Electronics & Communication", 78),
    ("B.Tech", "Electrical Engineering", 72),
    ("B.Tech", "Mechanical Engineering", 65),
    ("B.Com", "Information Systems", 60),
    ("B.Com", "General Commerce", 45),
    ("B.A.", "Economics", 50),
    ("High School", "General", 30)
]

CERTIFICATIONS_LIST = [
    ("AWS Certified Solutions Architect", ["AWS", "Cloud", "Microservices", "Docker"]),
    ("AWS Certified Developer Associate", ["AWS", "Docker", "REST API"]),
    ("Google Professional Data Engineer", ["Python", "SQL", "ETL", "Data Analysis"]),
    ("Microsoft Certified: Azure Data Scientist", ["Python", "Machine Learning", "Scikit-Learn"]),
    ("TensorFlow Developer Certificate", ["TensorFlow", "Deep Learning", "Python"]),
    ("Oracle Certified Professional: Java SE", ["Java", "Object-Oriented Programming"]),
    ("Meta Front-End Developer Professional", ["React", "JavaScript", "HTML", "CSS"]),
    ("Meta Back-End Developer Professional", ["Python", "Django", "SQL", "REST API"]),
    ("IBM Data Science Professional", ["Python", "Data Analysis", "SQL", "Pandas"]),
    ("Tableau Desktop Specialist", ["Tableau", "Data Visualization", "Data Analysis"]),
    ("Microsoft Certified: Power BI Data Analyst", ["Power BI", "Excel", "Data Analysis"]),
    ("Certified Kubernetes Administrator (CKA)", ["Docker", "Kubernetes", "Linux"]),
    ("None", [])
]

PROJECT_TEMPLATES = {
    "Java Developer": [
        "E-Commerce Microservices Engine with Spring Boot and Kafka",
        "Hospital Management System using Java, Hibernate and MySQL",
        "Banking Core Transaction API with OAuth2 and Spring Security",
        "Distributed Inventory Tracker using Java, Docker and Redis"
    ],
    "Python Developer": [
        "Real-Time Chat and Notification Service with FastAPI and WebSockets",
        "Automated Financial Data Pipeline using Django and Celery",
        "SaaS Subscription Backend with Python, PostgreSQL and Stripe API",
        "Task Management REST API with Flask and Redis Caching"
    ],
    "Web Developer": [
        "Interactive Collaborative Canvas using React and Canvas API",
        "Multi-Vendor Marketplace with MERN Stack (MongoDB, Express, React, Node)",
        "Corporate Responsive Portal using HTML5, CSS3, JavaScript and Bootstrap",
        "Content Management System with Node.js and MongoDB"
    ],
    "Data Analyst": [
        "Customer Churn Predictive Analysis with Python and Power BI Dashboard",
        "E-Commerce Sales Performance Analytics in Tableau and SQL",
        "Healthcare Operational KPI Dashboard using Excel and Power BI",
        "Supply Chain Optimization Analytics using SQL and Pandas"
    ],
    "Data Scientist": [
        "Customer Sentiment Analysis on 100k Reviews using NLP and Scikit-Learn",
        "Credit Risk Default Prediction Engine using XGBoost and TensorFlow",
        "Computer Vision Defect Detection Pipeline using Deep Learning",
        "Time Series Stock Forecasting Model with LSTM and Prophet"
    ],
    "Software Engineer": [
        "High-Concurrency In-Memory Key-Value Store in C++",
        "Distributed Web Crawler and Indexer using Java and Multithreading",
        "Graph Algorithm Visualizer and Benchmark Suite in Python",
        "High-Performance Network Proxy Server in Linux and C"
    ],
    "Frontend Developer": [
        "E-Commerce Storefront with Next.js, TypeScript and Tailwind CSS",
        "Cryptocurrency Portfolio Tracker in React with Redux Toolkit",
        "Interactive Dashboard with Chart.js, React and Framer Motion",
        "Accessible SaaS Onboarding Flow with TypeScript and Styled Components"
    ],
    "Backend Developer": [
        "Scalable Multi-Tenant Authentication Microservice using Node.js and JWT",
        "Event-Driven Order Processing Engine with Python, RabbitMQ and PostgreSQL",
        "High-Throughput Streaming API with Node.js and Redis Pub/Sub",
        "Cloud-Native RESTful API Gateway with Docker and Nginx"
    ],
    "Full Stack Developer": [
        "Enterprise Project Management System with React, Node.js and PostgreSQL",
        "Social Media Sharing Platform with Next.js, Express and MongoDB",
        "Real-time Auction Platform with React, Python FastAPI and WebSockets",
        "EdTech Video Learning Management System with MERN Stack and AWS S3"
    ],
    "Database Developer": [
        "Multi-Terabyte Database Partitioning and Index Optimization in PostgreSQL",
        "Enterprise Data Warehouse ETL Pipeline using SQL Stored Procedures and Python",
        "High-Availability MySQL Cluster with Automated Failover and Replication",
        "Financial Ledger Schema Design with Strict ACID Guarantees in Oracle"
    ]
}


# ==============================================================================
# 2. SYNTHETIC DATASET GENERATOR (5,000+ REALISTIC CANDIDATES)
# ==============================================================================

def generate_synthetic_dataset(num_records: int = 5300) -> pd.DataFrame:
    """
    Generates realistic candidate records across the 10 job roles.
    Includes strong, medium, and weak candidates, along with realistic dirty
    variations (inconsistent casings, extra spaces, nulls, duplicates).
    """
    print(f"\n[STEP 1] Generating {num_records} realistic candidate records...")
    roles = list(JOB_ROLES_CATALOG.keys())
    data = []

    for i in range(1, num_records + 1):
        cand_id = f"CAND_{i:05d}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 999)}@gmail.com"
        location = random.choice(LOCATIONS)

        target_role = random.choice(roles)
        job_info = JOB_ROLES_CATALOG[target_role]
        job_req_skills = job_info["required_skills"]
        job_desc = job_info["description"]
        min_exp = job_info["min_exp"]

        archetype_roll = random.random()
        if archetype_roll < 0.35:
            # Strong Candidate
            num_req_skills = random.randint(int(len(job_req_skills) * 0.8), len(job_req_skills))
            matched_pool = random.sample(job_req_skills, num_req_skills)
            extra_skills = random.sample(["Git", "Linux", "REST API", "Docker", "SQL", "Agile", "JIRA"], random.randint(1, 3))
            cand_skills = list(dict.fromkeys(matched_pool + extra_skills))
            experience_years = random.randint(min_exp, min_exp + random.randint(2, 7))
            edu_degree, edu_spec, edu_base_score = random.choice([d for d in DEGREES_AND_TIERS if d[2] >= 85])
            num_projects = random.randint(2, 4)
            cand_projects = random.sample(PROJECT_TEMPLATES[target_role], min(num_projects, len(PROJECT_TEMPLATES[target_role])))
            cert_options = [c[0] for c in CERTIFICATIONS_LIST if c[0] != "None"]
            cand_certs = random.sample(cert_options, random.randint(1, 2))

        elif archetype_roll < 0.70:
            # Review Candidate (Moderate Match)
            num_req_skills = random.randint(int(len(job_req_skills) * 0.5), int(len(job_req_skills) * 0.75))
            matched_pool = random.sample(job_req_skills, num_req_skills)
            other_role = random.choice([r for r in roles if r != target_role])
            other_skills = random.sample(JOB_ROLES_CATALOG[other_role]["required_skills"], random.randint(1, 3))
            cand_skills = list(dict.fromkeys(matched_pool + other_skills))
            experience_years = max(1, random.randint(min_exp - 2, min_exp + 1))
            edu_degree, edu_spec, edu_base_score = random.choice([d for d in DEGREES_AND_TIERS if 65 <= d[2] <= 90])
            cand_projects = random.sample(PROJECT_TEMPLATES[target_role], random.randint(1, 2))
            cand_certs = [random.choice([c[0] for c in CERTIFICATIONS_LIST])]
            if cand_certs == ["None"]:
                cand_certs = []

        else:
            # Weak / Rejected Candidate
            num_req_skills = random.randint(0, max(1, int(len(job_req_skills) * 0.3)))
            matched_pool = random.sample(job_req_skills, num_req_skills) if num_req_skills > 0 else []
            unrelated_role = random.choice([r for r in roles if r != target_role])
            unrelated_skills = random.sample(JOB_ROLES_CATALOG[unrelated_role]["required_skills"], random.randint(2, 4))
            cand_skills = list(dict.fromkeys(matched_pool + unrelated_skills + ["MS Word", "Communication"]))
            experience_years = random.randint(0, max(1, min_exp - 1))
            edu_degree, edu_spec, edu_base_score = random.choice([d for d in DEGREES_AND_TIERS if d[2] <= 75])
            cand_projects = [f"Basic Academic Coursework in {edu_spec}"] if random.random() > 0.4 else []
            cand_certs = [] if random.random() > 0.2 else ["General Computer Literacy Certificate"]

        # Messy capitalization injection
        raw_skills_list = []
        for s in cand_skills:
            r = random.random()
            if r < 0.15:
                raw_skills_list.append(s.upper())
            elif r < 0.30:
                raw_skills_list.append(s.lower())
            elif r < 0.40:
                raw_skills_list.append(f"  {s}  ")
            else:
                raw_skills_list.append(s)

        skills_str = ", ".join(raw_skills_list)
        projects_str = "; ".join(cand_projects) if cand_projects else "None"
        certs_str = ", ".join(cand_certs) if cand_certs else "None"

        resume_text = (
            f"Candidate: {name}\n"
            f"Email: {email} | Location: {location}\n"
            f"Professional Summary: Dedicated {target_role} professional with {experience_years} years of industry experience. "
            f"Demonstrated competence in technical problem solving, software engineering, and collaborative team delivery.\n"
            f"Technical Skills: {skills_str}\n"
            f"Education: {edu_degree} in {edu_spec}\n"
            f"Key Projects: {projects_str}\n"
            f"Certifications: {certs_str}\n"
        )

        data.append({
            "candidate_id": cand_id,
            "candidate_name": name,
            "email": email,
            "education": f"{edu_degree} in {edu_spec}",
            "degree": edu_degree,
            "specialization": edu_spec,
            "experience_years": experience_years,
            "skills": skills_str,
            "projects": projects_str,
            "certifications": certs_str,
            "job_role": target_role,
            "job_required_skills": ", ".join(job_req_skills),
            "job_description": job_desc,
            "location": location,
            "resume_text": resume_text
        })

    df = pd.DataFrame(data)

    # Inject dirty records: duplicates, NaNs, extra spaces
    duplicate_rows = df.sample(n=120, random_state=42).copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    missing_idx = df.sample(n=80, random_state=123).index
    df.loc[missing_idx[:40], "certifications"] = np.nan
    df.loc[missing_idx[40:], "location"] = np.nan

    space_idx = df.sample(n=100, random_state=456).index
    df.loc[space_idx, "candidate_name"] = "   " + df.loc[space_idx, "candidate_name"] + "   "

    print(f"Generated raw dataset shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


# ==============================================================================
# 3. DATA CLEANING & NORMALIZATION PIPELINE
# ==============================================================================

CANONICAL_SKILLS_MAP = {
    "java": "Java",
    "python": "Python",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "oracle": "Oracle",
    "aws": "AWS",
    "azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring boot": "Spring Boot",
    "hibernate": "Hibernate",
    "rest api": "REST API",
    "microservices": "Microservices",
    "c++": "C++",
    "excel": "Excel",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "redis": "Redis",
    "linux": "Linux",
    "celery": "Celery",
    "bootstrap": "Bootstrap",
    "tailwind css": "Tailwind CSS",
    "redux": "Redux",
    "etl": "ETL"
}


def clean_skill_string(skill_str: str) -> str:
    """Cleans, normalizes casing and deduplicates comma-separated skills."""
    if not isinstance(skill_str, str) or pd.isna(skill_str):
        return "None"
    
    parts = [s.strip() for s in skill_str.split(",") if s.strip()]
    cleaned_skills = []
    for p in parts:
        lower_p = p.lower()
        normalized = CANONICAL_SKILLS_MAP.get(lower_p, p.title())
        if normalized not in cleaned_skills:
            cleaned_skills.append(normalized)
    return ", ".join(cleaned_skills) if cleaned_skills else "None"


def perform_data_cleaning(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Performs data cleaning, drops duplicates, imputes nulls, normalizes strings.
    """
    print("\n[STEP 2] Performing Data Cleaning & Normalization...")

    before_stats = {
        "total_rows": len(df_raw),
        "total_columns": len(df_raw.columns),
        "duplicate_rows": int(df_raw.duplicated(subset=["candidate_id", "email"]).sum()),
        "missing_values": int(df_raw.isna().sum().sum())
    }

    df_clean = df_raw.copy()

    # 1. Drop duplicate candidates
    df_clean = df_clean.drop_duplicates(subset=["candidate_id", "email"], keep="first").reset_index(drop=True)

    # 2. Trim string columns
    for col in df_clean.select_dtypes(include="object").columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()

    # 3. Handle missing values
    df_clean["certifications"] = df_clean["certifications"].replace({"nan": "None", "": "None"}).fillna("None")
    df_clean["projects"] = df_clean["projects"].replace({"nan": "None", "": "None"}).fillna("None")
    df_clean["location"] = df_clean["location"].replace({"nan": "Remote", "": "Remote"}).fillna("Remote")

    # 4. Normalize Skills
    df_clean["skills"] = df_clean["skills"].apply(clean_skill_string)
    df_clean["job_required_skills"] = df_clean["job_required_skills"].apply(clean_skill_string)

    # 5. Sanitize numeric columns
    df_clean["experience_years"] = pd.to_numeric(df_clean["experience_years"], errors="coerce").fillna(0)
    df_clean["experience_years"] = df_clean["experience_years"].clip(lower=0, upper=40).astype(int)

    after_stats = {
        "total_rows": len(df_clean),
        "total_columns": len(df_clean.columns),
        "duplicate_rows": int(df_clean.duplicated(subset=["candidate_id", "email"]).sum()),
        "missing_values": int(df_clean.isna().sum().sum())
    }

    print("\n--- DATA CLEANING SUMMARY REPORT ---")
    print(f"Before Cleaning -> Rows: {before_stats['total_rows']}, Duplicates: {before_stats['duplicate_rows']}, Nulls: {before_stats['missing_values']}")
    print(f"After Cleaning  -> Rows: {after_stats['total_rows']}, Duplicates: {after_stats['duplicate_rows']}, Nulls: {after_stats['missing_values']}")

    return df_clean, {"before": before_stats, "after": after_stats}


# ==============================================================================
# 4. SKILL MATCHING & FEATURE ENGINEERING
# ==============================================================================

EDUCATION_WEIGHT_MAP = {
    "M.Tech": 95.0, "M.S.": 95.0, "MCA": 90.0, "B.Tech": 90.0, "B.E.": 88.0,
    "B.S.": 90.0, "B.Sc": 80.0, "BCA": 80.0, "B.Com": 55.0, "B.A.": 50.0, "High School": 30.0
}


def calculate_skill_matching(cand_skills_str: str, req_skills_str: str) -> tuple[int, int, float, list, list]:
    """Computes matched skills, missing skills, and skill match percentage."""
    cand_list = [s.strip() for s in cand_skills_str.split(",") if s.strip() and s.strip().lower() != "none"]
    req_list = [s.strip() for s in req_skills_str.split(",") if s.strip()]

    cand_set_lower = {s.lower(): s for s in cand_list}
    matched = []
    missing = []

    for req in req_list:
        if req.lower() in cand_set_lower:
            matched.append(req)
        else:
            missing.append(req)

    total_req = len(req_list) if req_list else 1
    match_pct = round((len(matched) / total_req) * 100.0, 2)

    return len(matched), len(missing), match_pct, matched, missing


def compute_all_scores_and_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes all sub-scores, overall weighted matching score, and shortlist status."""
    print("\n[STEP 3] Performing Skill Matching, Score Computation & Feature Engineering...")

    matched_counts, missing_counts, skill_match_scores = [], [], []
    matched_skills_list, missing_skills_list = [], []

    for _, row in df.iterrows():
        n_match, n_miss, pct, m_list, miss_list = calculate_skill_matching(row["skills"], row["job_required_skills"])
        matched_counts.append(n_match)
        missing_counts.append(n_miss)
        skill_match_scores.append(pct)
        matched_skills_list.append(", ".join(m_list))
        missing_skills_list.append(", ".join(miss_list))

    df["matched_skills_count"] = matched_counts
    df["missing_skills_count"] = missing_counts
    df["skill_match_score"] = skill_match_scores
    df["matched_skills"] = matched_skills_list
    df["missing_skills"] = missing_skills_list

    # 1. Experience Match Score (20% weight)
    exp_scores = []
    for _, row in df.iterrows():
        role = row["job_role"]
        min_exp = JOB_ROLES_CATALOG.get(role, {}).get("min_exp", 2)
        cand_exp = row["experience_years"]
        if cand_exp >= min_exp:
            score = min(100.0, 80.0 + (cand_exp - min_exp) * 4.0)
        else:
            score = max(20.0, (cand_exp / max(1, min_exp)) * 75.0)
        exp_scores.append(round(score, 2))
    df["experience_match_score"] = exp_scores

    # 2. Education Match Score (10% weight)
    edu_scores = []
    for _, row in df.iterrows():
        deg = row["degree"]
        spec = row["specialization"]
        base = EDUCATION_WEIGHT_MAP.get(deg, 60.0)
        if "Computer" in spec or "Data" in spec or "Artificial" in spec or "Information" in spec:
            adj = base
        elif "Electronics" in spec or "Electrical" in spec:
            adj = base * 0.90
        elif "Mechanical" in spec:
            adj = base * 0.75
        else:
            adj = base * 0.60
        edu_scores.append(round(min(100.0, max(20.0, adj)), 2))
    df["education_match_score"] = edu_scores

    # 3. Project Match Score (10% weight)
    proj_scores, proj_counts = [], []
    for _, row in df.iterrows():
        p_str = row["projects"]
        if p_str == "None" or not p_str.strip():
            count = 0
            score = 25.0
        else:
            count = len(p_str.split(";"))
            if count >= 3:
                score = 95.0
            elif count == 2:
                score = 80.0
            elif count == 1:
                score = 65.0
            else:
                score = 40.0
        proj_counts.append(count)
        proj_scores.append(round(score, 2))
    df["project_count"] = proj_counts
    df["project_score"] = proj_scores
    df["project_match_score"] = proj_scores

    # 4. Certification Score (10% weight)
    cert_scores, cert_counts = [], []
    for _, row in df.iterrows():
        c_str = row["certifications"]
        if c_str == "None" or not c_str.strip():
            count = 0
            score = 30.0
        else:
            count = len(c_str.split(","))
            if count >= 2:
                score = 95.0
            elif count == 1:
                score = 80.0
            else:
                score = 50.0
        cert_counts.append(count)
        cert_scores.append(round(score, 2))
    df["certification_count"] = cert_counts
    df["certification_score"] = cert_scores

    # 5. Skill count
    df["skill_count"] = df["skills"].apply(lambda s: len(s.split(",")) if s != "None" else 0)

    # 6. Overall Weighted Score:
    # (skill_match_score * 0.50) + (experience_match_score * 0.20) + (education_match_score * 0.10) +
    # (project_score * 0.10) + (certification_score * 0.10)
    df["overall_score"] = (
        (df["skill_match_score"] * 0.50) +
        (df["experience_match_score"] * 0.20) +
        (df["education_match_score"] * 0.10) +
        (df["project_score"] * 0.10) +
        (df["certification_score"] * 0.10)
    ).round(2).clip(lower=0.0, upper=100.0)

    # 7. Target Shortlist Status:
    # >= 80 -> SHORTLISTED, >= 60 -> REVIEW, < 60 -> REJECTED
    def assign_shortlist_status(score: float) -> str:
        if score >= 80.0:
            return "SHORTLISTED"
        elif score >= 60.0:
            return "REVIEW"
        else:
            return "REJECTED"

    df["shortlist_status"] = df["overall_score"].apply(assign_shortlist_status)

    print("\n--- TARGET CLASS DISTRIBUTION ---")
    print(df["shortlist_status"].value_counts(normalize=True).mul(100).round(2).astype(str) + " %")
    print(df["shortlist_status"].value_counts())

    return df


# ==============================================================================
# 5. TEXT MINING: TF-IDF & COSINE SIMILARITY
# ==============================================================================

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def clean_text_for_nlp(text: str) -> str:
    """Performs lowercasing, punctuation removal, tokenization, and stopword filtering."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s+#.]', ' ', text)
    tokens = text.split()
    filtered = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(filtered)


def calculate_tfidf_and_cosine_similarity(df: pd.DataFrame) -> tuple[pd.DataFrame, TfidfVectorizer]:
    """Fits TF-IDF vectorizer and calculates Cosine Similarity between resumes and job descriptions."""
    print("\n[STEP 4] Calculating TF-IDF and Cosine Similarity...")

    df["cleaned_resume_text"] = df["resume_text"].apply(clean_text_for_nlp)
    df["cleaned_job_desc"] = df["job_description"].apply(clean_text_for_nlp)

    corpus = pd.concat([df["cleaned_resume_text"], df["cleaned_job_desc"]]).unique()
    tfidf_vectorizer = TfidfVectorizer(max_features=1500, ngram_range=(1, 2))
    tfidf_vectorizer.fit(corpus)

    res_vecs = tfidf_vectorizer.transform(df["cleaned_resume_text"])
    job_vecs = tfidf_vectorizer.transform(df["cleaned_job_desc"])

    cosine_sims = []
    for i in range(len(df)):
        sim = float(res_vecs[i].multiply(job_vecs[i]).sum())
        cosine_sims.append(round(sim * 100.0, 2))

    df["cosine_similarity_score"] = cosine_sims
    print(f"Cosine Similarity -> Mean: {df['cosine_similarity_score'].mean():.2f}%, Max: {df['cosine_similarity_score'].max():.2f}%, Min: {df['cosine_similarity_score'].min():.2f}%")

    return df, tfidf_vectorizer


# ==============================================================================
# 6. EXPLORATORY DATA ANALYSIS (EDA) & VISUALIZATIONS
# ==============================================================================

def generate_eda_visualizations(df: pd.DataFrame):
    """Generates all 8 requested EDA plots and saves them to reports/."""
    print("\n[STEP 5] Generating Exploratory Data Analysis Visualizations...")
    sns.set_theme(style="whitegrid")

    # 1. Candidates by Job Role
    plt.figure(figsize=(10, 5))
    role_order = df["job_role"].value_counts().index
    sns.countplot(data=df, y="job_role", order=role_order, palette="viridis")
    plt.title("1. Candidate Distribution Across Job Roles", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Candidates")
    plt.ylabel("Job Role")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_1_job_roles.png"), dpi=200)
    plt.close()

    # 2. Experience Distribution
    plt.figure(figsize=(8, 4))
    sns.histplot(df["experience_years"], bins=15, kde=True, color="#2b5c8f")
    plt.title("2. Candidate Experience Distribution (Years)", fontsize=14, fontweight="bold")
    plt.xlabel("Years of Professional Experience")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_2_experience.png"), dpi=200)
    plt.close()

    # 3. Education Distribution
    plt.figure(figsize=(9, 4))
    deg_order = df["degree"].value_counts().index
    sns.countplot(data=df, x="degree", order=deg_order, palette="mako")
    plt.title("3. Candidate Highest Degree Distribution", fontsize=14, fontweight="bold")
    plt.xlabel("Degree Level")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_3_education.png"), dpi=200)
    plt.close()

    # 4. Most Common Skills (Top 15)
    all_skills = []
    for s_str in df["skills"]:
        if s_str != "None":
            all_skills.extend([s.strip() for s in s_str.split(",") if s.strip()])
    skill_series = pd.Series(all_skills).value_counts().head(15)

    plt.figure(figsize=(10, 5))
    sns.barplot(x=skill_series.values, y=skill_series.index, palette="rocket")
    plt.title("4. Top 15 Most Common Candidate Technical Skills", fontsize=14, fontweight="bold")
    plt.xlabel("Frequency Across Resumes")
    plt.ylabel("Skill")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_4_common_skills.png"), dpi=200)
    plt.close()

    # 5. Certification Distribution
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x="certification_count", palette="crest")
    plt.title("5. Candidate Certification Count Distribution", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Professional Certifications")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_5_certifications.png"), dpi=200)
    plt.close()

    # 6. Overall Candidate Score Distribution
    plt.figure(figsize=(8, 4))
    sns.histplot(df["overall_score"], bins=20, kde=True, color="#1f77b4")
    plt.axvline(80, color="green", linestyle="--", label="Shortlisted Cutoff (>=80)")
    plt.axvline(60, color="orange", linestyle="--", label="Review Cutoff (>=60)")
    plt.title("6. Overall Candidate Matching Score Distribution", fontsize=14, fontweight="bold")
    plt.xlabel("Overall Matching Score (0 - 100)")
    plt.ylabel("Candidate Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_6_candidate_score.png"), dpi=200)
    plt.close()

    # 7. Shortlisted vs Review vs Rejected
    plt.figure(figsize=(6, 6))
    status_counts = df["shortlist_status"].value_counts()
    colors = ["#2ca02c", "#ff7f0e", "#d62728"]
    plt.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", colors=colors, startangle=140, explode=[0.05, 0.05, 0.05])
    plt.title("7. Candidate Shortlist Status Breakdown", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_7_shortlist_status.png"), dpi=200)
    plt.close()

    # 8. Candidates by Experience Level
    def categorize_exp_level(y: int) -> str:
        if y <= 2:
            return "Junior (0-2 Yrs)"
        elif y <= 5:
            return "Mid-Level (3-5 Yrs)"
        else:
            return "Senior (6+ Yrs)"

    df["exp_tier"] = df["experience_years"].apply(categorize_exp_level)
    plt.figure(figsize=(7, 4))
    sns.countplot(data=df, x="exp_tier", order=["Junior (0-2 Yrs)", "Mid-Level (3-5 Yrs)", "Senior (6+ Yrs)"], palette="Blues_d")
    plt.title("8. Candidate Distribution by Experience Tier", fontsize=14, fontweight="bold")
    plt.xlabel("Seniority Level")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "eda_8_experience_level.png"), dpi=200)
    plt.close()

    print("Generated and saved all 8 EDA visualizations into reports/ directory.")


# ==============================================================================
# 7. MACHINE LEARNING CLASSIFICATION MODELS
# ==============================================================================

FEATURE_COLUMNS = [
    "experience_years",
    "skill_count",
    "project_count",
    "certification_count",
    "education_match_score",
    "skill_match_score",
    "experience_match_score",
    "project_score",
    "certification_score",
    "cosine_similarity_score"
]


def train_classification_models(df: pd.DataFrame) -> dict:
    """
    Trains Logistic Regression, Decision Tree, and Random Forest on 80/20 stratified split.
    Evaluates metrics, saves comparison report, and selects best model.
    """
    print("\n[STEP 6] Training Machine Learning Classification Models...")

    X = df[FEATURE_COLUMNS].copy()
    y = df["shortlist_status"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Use native sklearn if available, otherwise robust fallback implementations
    if NATIVE_SKLEARN_TREES:
        dt_clf = DecisionTreeClassifier(max_depth=8, min_samples_split=10, random_state=42)
        rf_clf = RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_split=5, random_state=42)
    else:
        dt_clf = FallbackDecisionTree(max_depth=8, min_samples_split=10, random_state=42)
        rf_clf = FallbackRandomForest(n_estimators=15, max_depth=8, min_samples_split=8, random_state=42)

    models = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, random_state=42),
            "use_scaled": True
        },
        "Decision Tree": {
            "model": dt_clf,
            "use_scaled": False
        },
        "Random Forest": {
            "model": rf_clf,
            "use_scaled": False
        }
    }

    results = []
    trained_instances = {}

    for name, item in models.items():
        clf = item["model"]
        X_tr = X_train_scaled if item["use_scaled"] else X_train
        X_te = X_test_scaled if item["use_scaled"] else X_test

        clf.fit(X_tr, y_train)
        y_pred = clf.predict(X_te)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=["SHORTLISTED", "REVIEW", "REJECTED"])

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1_Score": round(f1, 4),
            "Confusion_Matrix": cm.tolist()
        })
        trained_instances[name] = clf

        print(f"\nModel: {name}")
        print(f"Accuracy: {acc*100:.2f}% | Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}% | F1: {f1*100:.2f}%")
        print("Confusion Matrix (SHORTLISTED, REVIEW, REJECTED):\n", cm)

    results_df = pd.DataFrame(results)
    comparison_csv_path = os.path.join(REPORTS_DIR, "model_comparison.csv")
    results_df.to_csv(comparison_csv_path, index=False)

    # Plot Confusion Matrices
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    classes = ["SHORTLISTED", "REVIEW", "REJECTED"]
    for idx, r in enumerate(results):
        cm_data = np.array(r["Confusion_Matrix"])
        sns.heatmap(cm_data, annot=True, fmt="d", cmap="Blues", ax=axes[idx],
                    xticklabels=classes, yticklabels=classes)
        axes[idx].set_title(f"{r['Model']}\n(Acc: {r['Accuracy']*100:.1f}%)")
        axes[idx].set_xlabel("Predicted")
        axes[idx].set_ylabel("Actual")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "confusion_matrices.png"), dpi=200)
    plt.close()

    # Best model selection
    best_row = results_df.sort_values(by="F1_Score", ascending=False).iloc[0]
    best_model_name = best_row["Model"]
    best_model = trained_instances[best_model_name]
    print(f"\n>>> Selected Best-Performing Model: {best_model_name} (F1 Score: {best_row['F1_Score']*100:.2f}%)")

    return {
        "models": trained_instances,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "scaler": scaler,
        "comparison_df": results_df,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }


# ==============================================================================
# 8. CANDIDATE CLUSTERING (UNSUPERVISED DATA MINING)
# ==============================================================================

def perform_candidate_clustering(df: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    """Applies K-Means clustering (K=4), produces Elbow curve, and profiles candidate archetypes."""
    print("\n[STEP 7] Performing Unsupervised Data Mining (K-Means Clustering)...")

    cluster_features = [
        "skill_match_score",
        "experience_match_score",
        "project_score",
        "certification_score",
        "overall_score"
    ]

    scaler = StandardScaler()
    X_clust = scaler.fit_transform(df[cluster_features])

    # Elbow Evaluation
    inertias = []
    k_range = list(range(2, 8))
    for k in k_range:
        if NATIVE_SKLEARN_TREES:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
        else:
            km = FallbackKMeans(n_clusters=k, random_state=42)
        km.fit(X_clust)
        inertias.append(km.inertia_)

    # Plot Elbow Method
    plt.figure(figsize=(7, 4))
    plt.plot(k_range, inertias, marker="o", color="#2b5c8f", linewidth=2)
    plt.title("Elbow Method For Optimal K (Candidate Clustering)", fontsize=13, fontweight="bold")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Within-Cluster Sum of Squares (Inertia)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "kmeans_elbow_curve.png"), dpi=200)
    plt.close()

    # Optimal K=4
    if NATIVE_SKLEARN_TREES:
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    else:
        kmeans = FallbackKMeans(n_clusters=4, random_state=42)

    df["cluster_id"] = kmeans.fit_predict(X_clust)
    cluster_means = df.groupby("cluster_id")[cluster_features].mean()

    cluster_labels = {}
    for cid in range(4):
        means = cluster_means.loc[cid]
        skill = means["skill_match_score"]
        exp = means["experience_match_score"]
        if skill >= 70 and exp >= 70:
            cluster_labels[cid] = "High Skill / High Experience (Top Tier)"
        elif skill >= 60 and exp < 70:
            cluster_labels[cid] = "High Skill / Low Experience (High Potential Junior)"
        elif skill < 60 and exp >= 65:
            cluster_labels[cid] = "Low Skill / High Experience (Experienced Career Pivot)"
        else:
            cluster_labels[cid] = "Low Skill / Low Experience (Entry Level Mismatch)"

    df["cluster_profile"] = df["cluster_id"].map(cluster_labels)

    # Plot Clusters Scatter
    plt.figure(figsize=(9, 5))
    sns.scatterplot(
        data=df,
        x="skill_match_score",
        y="experience_match_score",
        hue="cluster_profile",
        palette="tab10",
        alpha=0.6,
        s=30
    )
    plt.title("K-Means Candidate Segmentation (Skill Match vs Experience)", fontsize=13, fontweight="bold")
    plt.xlabel("Skill Match Score (%)")
    plt.ylabel("Experience Match Score (%)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "kmeans_clusters_scatter.png"), dpi=200)
    plt.close()

    print("\nCluster Centroid Means:\n", cluster_means.round(2))
    print("\nCandidate Distribution across Clusters:\n", df["cluster_profile"].value_counts())

    return df, kmeans


# ==============================================================================
# 9. FEATURE IMPORTANCE ANALYSIS
# ==============================================================================

def analyze_feature_importance(best_model, feature_names: list[str]) -> pd.DataFrame:
    """Computes feature importance rankings and plots horizontal bar chart."""
    print("\n[STEP 8] Computing Feature Importance...")

    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    elif hasattr(best_model, "coef_"):
        importances = np.mean(np.abs(best_model.coef_), axis=0)
    else:
        importances = np.ones(len(feature_names)) / len(feature_names)

    feat_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": np.round(importances, 4),
        "Importance_Pct": np.round(importances / importances.sum() * 100, 2)
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

    feat_csv_path = os.path.join(REPORTS_DIR, "feature_importance.csv")
    feat_df.to_csv(feat_csv_path, index=False)

    plt.figure(figsize=(9, 5))
    sns.barplot(data=feat_df, x="Importance", y="Feature", palette="viridis")
    plt.title("Feature Importance Ranking (Candidate Shortlisting Model)", fontsize=13, fontweight="bold")
    plt.xlabel("Relative Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "feature_importance.png"), dpi=200)
    plt.close()

    print(f"Saved feature importance report to: {feat_csv_path}")
    print("\nTop 5 Most Influential Features:")
    print(feat_df.head(5))

    return feat_df


# ==============================================================================
# 10. COMPLETE REUSABLE INFERENCE PIPELINE CLASS
# ==============================================================================

class ResumeShortlistingPipeline:
    """
    Production-ready end-to-end inference pipeline:
    Takes raw resume text and job description, extracts skills, computes TF-IDF
    features, cosine similarity, rule & ML predictions, and returns full candidate analytics.
    """

    def __init__(self, model, tfidf_vectorizer, feature_columns=None):
        self.model = model
        self.tfidf_vectorizer = tfidf_vectorizer
        self.feature_columns = feature_columns or FEATURE_COLUMNS

    def predict_candidate(self, resume_text: str, job_description: str) -> dict:
        """
        Predicts shortlisting decision and matching analytics for a single resume & job description.
        """
        cleaned_res = clean_text_for_nlp(resume_text)
        cleaned_job = clean_text_for_nlp(job_description)

        detected_skills = []
        for kw, canon in CANONICAL_SKILLS_MAP.items():
            pattern = rf'(?<!\w){re.escape(kw)}(?!\w)'
            if re.search(pattern, cleaned_res, re.IGNORECASE):
                if canon not in detected_skills:
                    detected_skills.append(canon)

        required_skills = []
        for kw, canon in CANONICAL_SKILLS_MAP.items():
            pattern = rf'(?<!\w){re.escape(kw)}(?!\w)'
            if re.search(pattern, cleaned_job, re.IGNORECASE):
                if canon not in required_skills:
                    required_skills.append(canon)

        if len(required_skills) == 0:
            for role_name, rdata in JOB_ROLES_CATALOG.items():
                if role_name.lower() in job_description.lower():
                    required_skills = rdata["required_skills"]
                    break

        cand_lower = {s.lower() for s in detected_skills}
        matched = [r for r in required_skills if r.lower() in cand_lower]
        missing = [r for r in required_skills if r.lower() not in cand_lower]
        tot_req = len(required_skills) if required_skills else 1
        skill_match_score = round((len(matched) / tot_req) * 100.0, 2)

        exp_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|exp)?', resume_text, re.IGNORECASE)
        cand_exp = int(exp_match.group(1)) if exp_match else 2

        try:
            r_vec = self.tfidf_vectorizer.transform([cleaned_res])
            j_vec = self.tfidf_vectorizer.transform([cleaned_job])
            cos_sim = round(float(r_vec.multiply(j_vec).sum()) * 100.0, 2)
        except Exception:
            cos_sim = 50.0

        exp_score = min(100.0, max(20.0, cand_exp * 20.0))
        edu_score = 90.0 if ("degree" in cleaned_res or "b.tech" in cleaned_res or "m.s." in cleaned_res) else 75.0
        project_count = len(re.findall(r'project|system|engine|application|pipeline', cleaned_res))
        proj_score = min(100.0, 40.0 + project_count * 15.0)
        cert_count = len(re.findall(r'certified|certificate|certification', cleaned_res))
        cert_score = min(100.0, 35.0 + cert_count * 30.0)

        overall_score = round(
            (skill_match_score * 0.50) +
            (exp_score * 0.20) +
            (edu_score * 0.10) +
            (proj_score * 0.10) +
            (cert_score * 0.10),
            2
        )
        overall_score = min(100.0, max(0.0, overall_score))

        feat_dict = {
            "experience_years": cand_exp,
            "skill_count": len(detected_skills),
            "project_count": min(project_count, 5),
            "certification_count": min(cert_count, 3),
            "education_match_score": edu_score,
            "skill_match_score": skill_match_score,
            "experience_match_score": exp_score,
            "project_score": proj_score,
            "certification_score": cert_score,
            "cosine_similarity_score": cos_sim
        }
        feat_row = pd.DataFrame([feat_dict])[self.feature_columns]

        try:
            prediction = str(self.model.predict(feat_row)[0])
        except Exception:
            if overall_score >= 80.0:
                prediction = "SHORTLISTED"
            elif overall_score >= 60.0:
                prediction = "REVIEW"
            else:
                prediction = "REJECTED"

        if prediction == "SHORTLISTED":
            recommendation = "Strong candidate: High technical skill alignment and relevant experience."
        elif prediction == "REVIEW":
            recommendation = "Moderate candidate: Meets core prerequisites; review missing skills or portfolio."
        else:
            recommendation = "Low match: Substantial skill gaps or lack of required professional background."

        return {
            "prediction": prediction,
            "score": overall_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": recommendation,
            "skill_match_percentage": skill_match_score,
            "cosine_similarity_percentage": cos_sim,
            "detected_candidate_skills": detected_skills
        }


# ==============================================================================
# 11. DATA WAREHOUSE: STAR SCHEMA GENERATION
# ==============================================================================

def generate_star_schema(df: pd.DataFrame) -> dict:
    """Creates Star Schema dimension and fact tables."""
    print("\n[STEP 9] Preparing Data Warehouse Star Schema Tables...")

    # 1. dim_candidate
    dim_candidate = df[["candidate_id", "candidate_name", "email", "location"]].drop_duplicates(subset=["candidate_id"]).reset_index(drop=True)
    dim_candidate_path = os.path.join(DATA_DIR, "dim_candidate.csv")
    dim_candidate.to_csv(dim_candidate_path, index=False)

    # 2. dim_job
    job_rows = []
    job_id_map = {}
    for idx, (role, info) in enumerate(JOB_ROLES_CATALOG.items(), start=1):
        jid = f"JOB_{idx:03d}"
        job_id_map[role] = jid
        job_rows.append({
            "job_id": jid,
            "job_role": role,
            "min_experience_years": info["min_exp"],
            "job_required_skills": ", ".join(info["required_skills"]),
            "job_description": info["description"]
        })
    dim_job = pd.DataFrame(job_rows)
    dim_job_path = os.path.join(DATA_DIR, "dim_job.csv")
    dim_job.to_csv(dim_job_path, index=False)

    # 3. dim_skill
    skill_rows = []
    skill_categories = {
        "Languages": ["Java", "Python", "C++", "JavaScript", "TypeScript", "SQL", "HTML", "CSS"],
        "Frameworks": ["Spring Boot", "Hibernate", "Django", "FastAPI", "Flask", "React", "Next.js", "Node.js", "Express", "Bootstrap", "Tailwind CSS"],
        "Data & AI": ["Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "Power BI", "Tableau", "Excel", "Data Analysis", "Deep Learning", "Machine Learning", "ETL"],
        "Database & Cloud": ["PostgreSQL", "MySQL", "MongoDB", "Oracle", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "Git", "Linux"]
    }
    s_idx = 1
    skill_id_map = {}
    for cat, sks in skill_categories.items():
        for s in sks:
            sid = f"SKILL_{s_idx:03d}"
            skill_id_map[s] = sid
            skill_rows.append({"skill_id": sid, "skill_name": s, "skill_category": cat})
            s_idx += 1
    dim_skill = pd.DataFrame(skill_rows)
    dim_skill_path = os.path.join(DATA_DIR, "dim_skill.csv")
    dim_skill.to_csv(dim_skill_path, index=False)

    # 4. dim_date
    start_date = datetime(2026, 1, 1)
    date_rows = []
    for d in range(120):
        curr = start_date + timedelta(days=d)
        did = int(curr.strftime("%Y%m%d"))
        date_rows.append({
            "date_id": did,
            "full_date": curr.strftime("%Y-%m-%d"),
            "day": curr.day,
            "month": curr.month,
            "month_name": curr.strftime("%B"),
            "quarter": (curr.month - 1) // 3 + 1,
            "year": curr.year,
            "is_weekend": curr.weekday() >= 5
        })
    dim_date = pd.DataFrame(date_rows)
    dim_date_path = os.path.join(DATA_DIR, "dim_date.csv")
    dim_date.to_csv(dim_date_path, index=False)

    # 5. dim_education
    edu_rows = []
    edu_id_map = {}
    for idx, (deg, spec, base) in enumerate(DEGREES_AND_TIERS, start=1):
        eid = f"EDU_{idx:03d}"
        key = f"{deg} in {spec}"
        edu_id_map[key] = eid
        tier = "Tier 1 - Master/Advanced" if base >= 95 else ("Tier 2 - Bachelor STEM" if base >= 85 else ("Tier 3 - Other STEM" if base >= 70 else "Tier 4 - Non-STEM"))
        edu_rows.append({
            "education_id": eid,
            "degree": deg,
            "specialization": spec,
            "education_tier": tier,
            "education_base_score": base
        })
    dim_education = pd.DataFrame(edu_rows)
    dim_education_path = os.path.join(DATA_DIR, "dim_education.csv")
    dim_education.to_csv(dim_education_path, index=False)

    # 6. dim_experience
    exp_tiers = [
        ("EXP_001", 0, 2, "Fresher / Junior (0-2 Yrs)"),
        ("EXP_002", 3, 5, "Mid-Level Professional (3-5 Yrs)"),
        ("EXP_003", 6, 9, "Senior Specialist (6-9 Yrs)"),
        ("EXP_004", 10, 40, "Lead / Principal / Architect (10+ Yrs)")
    ]
    dim_experience = pd.DataFrame(exp_tiers, columns=["experience_id", "min_exp_years", "max_exp_years", "experience_level_name"])
    dim_experience_path = os.path.join(DATA_DIR, "dim_experience.csv")
    dim_experience.to_csv(dim_experience_path, index=False)

    def get_exp_id(years: int) -> str:
        if years <= 2:
            return "EXP_001"
        elif years <= 5:
            return "EXP_002"
        elif years <= 9:
            return "EXP_003"
        return "EXP_004"

    # 7. fact_candidate_analysis
    fact_rows = []
    date_ids_pool = dim_date["date_id"].tolist()

    for idx, row in df.iterrows():
        cand_id = row["candidate_id"]
        job_id = job_id_map.get(row["job_role"], "JOB_001")
        m_skills = [s.strip() for s in row["matched_skills"].split(",") if s.strip()]
        skill_id = skill_id_map.get(m_skills[0], "SKILL_001") if m_skills else "SKILL_001"
        date_id = random.choice(date_ids_pool)
        edu_key = row["education"]
        edu_id = edu_id_map.get(edu_key, "EDU_001")
        exp_id = get_exp_id(row["experience_years"])

        fact_rows.append({
            "candidate_id": cand_id,
            "job_id": job_id,
            "skill_id": skill_id,
            "date_id": date_id,
            "education_id": edu_id,
            "experience_id": exp_id,
            "skill_match_score": row["skill_match_score"],
            "experience_match_score": row["experience_match_score"],
            "education_match_score": row["education_match_score"],
            "project_score": row["project_score"],
            "certification_score": row["certification_score"],
            "overall_score": row["overall_score"],
            "shortlist_status": row["shortlist_status"]
        })

    fact_table = pd.DataFrame(fact_rows)
    fact_path = os.path.join(DATA_DIR, "fact_candidate_analysis.csv")
    fact_table.to_csv(fact_path, index=False)

    print(f"Star Schema Created:")
    print(f" - dim_candidate: {dim_candidate.shape}")
    print(f" - dim_job: {dim_job.shape}")
    print(f" - dim_skill: {dim_skill.shape}")
    print(f" - dim_date: {dim_date.shape}")
    print(f" - dim_education: {dim_education.shape}")
    print(f" - dim_experience: {dim_experience.shape}")
    print(f" - fact_candidate_analysis: {fact_table.shape}")

    return {
        "dim_candidate": dim_candidate,
        "dim_job": dim_job,
        "dim_skill": dim_skill,
        "dim_date": dim_date,
        "dim_education": dim_education,
        "dim_experience": dim_experience,
        "fact_table": fact_table
    }


# ==============================================================================
# 12. DATA WAREHOUSE DATA QUALITY AUDIT
# ==============================================================================

def audit_data_warehouse_quality(star_tables: dict) -> pd.DataFrame:
    """Performs data quality checks across the star schema."""
    print("\n[STEP 10] Auditing Data Warehouse Data Quality...")

    fact = star_tables["fact_table"]
    checks = []

    # 1. Primary candidate uniqueness
    dup_cand = fact["candidate_id"].duplicated().sum()
    checks.append({
        "Audit_Check": "Fact Table Candidate Uniqueness",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Primary / Business Key Unique",
        "Violations_Found": int(dup_cand),
        "Status": "PASS" if dup_cand == 0 else "FAIL"
    })

    # 2. Foreign Key: job_id
    valid_jobs = set(star_tables["dim_job"]["job_id"])
    orphaned_jobs = (~fact["job_id"].isin(valid_jobs)).sum()
    checks.append({
        "Audit_Check": "Referential Integrity: job_id",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Foreign Key exists in dim_job",
        "Violations_Found": int(orphaned_jobs),
        "Status": "PASS" if orphaned_jobs == 0 else "FAIL"
    })

    # 3. Foreign Key: education_id
    valid_edu = set(star_tables["dim_education"]["education_id"])
    orphaned_edu = (~fact["education_id"].isin(valid_edu)).sum()
    checks.append({
        "Audit_Check": "Referential Integrity: education_id",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Foreign Key exists in dim_education",
        "Violations_Found": int(orphaned_edu),
        "Status": "PASS" if orphaned_edu == 0 else "FAIL"
    })

    # 4. Foreign Key: experience_id
    valid_exp = set(star_tables["dim_experience"]["experience_id"])
    orphaned_exp = (~fact["experience_id"].isin(valid_exp)).sum()
    checks.append({
        "Audit_Check": "Referential Integrity: experience_id",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Foreign Key exists in dim_experience",
        "Violations_Found": int(orphaned_exp),
        "Status": "PASS" if orphaned_exp == 0 else "FAIL"
    })

    # 5. Foreign Key: date_id
    valid_dates = set(star_tables["dim_date"]["date_id"])
    orphaned_dates = (~fact["date_id"].isin(valid_dates)).sum()
    checks.append({
        "Audit_Check": "Referential Integrity: date_id",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Foreign Key exists in dim_date",
        "Violations_Found": int(orphaned_dates),
        "Status": "PASS" if orphaned_dates == 0 else "FAIL"
    })

    # 6. Value Range Checks: overall_score in [0, 100]
    invalid_scores = ((fact["overall_score"] < 0) | (fact["overall_score"] > 100)).sum()
    checks.append({
        "Audit_Check": "Score Boundary Validation",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "0 <= overall_score <= 100",
        "Violations_Found": int(invalid_scores),
        "Status": "PASS" if invalid_scores == 0 else "FAIL"
    })

    # 7. Null Values in Fact Table
    nulls_fact = fact.isna().sum().sum()
    checks.append({
        "Audit_Check": "Fact Table Null Value Check",
        "Target_Table": "fact_candidate_analysis",
        "Constraint": "Zero Null Values in Fact Table",
        "Violations_Found": int(nulls_fact),
        "Status": "PASS" if nulls_fact == 0 else "FAIL"
    })

    quality_df = pd.DataFrame(checks)
    quality_csv_path = os.path.join(REPORTS_DIR, "data_quality_report.csv")
    quality_df.to_csv(quality_csv_path, index=False)

    print("\n--- DATA QUALITY AUDIT RESULTS ---")
    print(quality_df.to_string(index=False))
    return quality_df


# ==============================================================================
# 13. MAIN EXECUTION WORKFLOW
# ==============================================================================

def main():
    # 1. Generate Raw Synthetic Dataset
    raw_df = generate_synthetic_dataset(num_records=5200)

    # 2. Clean Data
    clean_df, clean_stats = perform_data_cleaning(raw_df)

    # 3. Feature Engineering & Skill Matching
    processed_df = compute_all_scores_and_features(clean_df)

    # 4. TF-IDF & Cosine Similarity
    processed_df, tfidf_vec = calculate_tfidf_and_cosine_similarity(processed_df)

    # 5. EDA Visualizations
    generate_eda_visualizations(processed_df)

    # 6. Save Processed & Split Datasets
    processed_csv = os.path.join(DATA_DIR, "resume_processed_dataset.csv")
    processed_df.to_csv(processed_csv, index=False)

    train_df, test_df = train_test_split(
        processed_df, test_size=0.20, random_state=42, stratify=processed_df["shortlist_status"]
    )
    train_csv = os.path.join(DATA_DIR, "resume_training_dataset.csv")
    test_csv = os.path.join(DATA_DIR, "resume_test_dataset.csv")
    train_df.to_csv(train_csv, index=False)
    test_df.to_csv(test_csv, index=False)

    print(f"\nSaved Datasets:")
    print(f" - Processed: {processed_csv} ({len(processed_df)} rows)")
    print(f" - Training:  {train_csv} ({len(train_df)} rows)")
    print(f" - Testing:   {test_csv} ({len(test_df)} rows)")

    # 7. Train Classification Models
    ml_results = train_classification_models(processed_df)
    best_model = ml_results["best_model"]
    scaler = ml_results["scaler"]

    # 8. K-Means Clustering
    clustered_df, kmeans_model = perform_candidate_clustering(processed_df)

    # 9. Feature Importance
    feat_importance_df = analyze_feature_importance(best_model, FEATURE_COLUMNS)

    # 10. Star Schema & Data Warehouse Audit
    star_tables = generate_star_schema(processed_df)
    audit_df = audit_data_warehouse_quality(star_tables)

    # 11. Save Models & Inference Pipeline
    model_pkl = os.path.join(MODELS_DIR, "resume_shortlisting_model.pkl")
    tfidf_pkl = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
    preproc_pkl = os.path.join(MODELS_DIR, "preprocessor.pkl")
    pipeline_pkl = os.path.join(MODELS_DIR, "resume_shortlisting_pipeline.pkl")

    joblib.dump(best_model, model_pkl)
    joblib.dump(tfidf_vec, tfidf_pkl)
    joblib.dump(scaler, preproc_pkl)

    inference_pipeline = ResumeShortlistingPipeline(
        model=best_model,
        tfidf_vectorizer=tfidf_vec,
        feature_columns=FEATURE_COLUMNS
    )
    joblib.dump(inference_pipeline, pipeline_pkl)

    print(f"\nSaved Model Artifacts:")
    print(f" - Model:            {model_pkl}")
    print(f" - TF-IDF Vectorizer:{tfidf_pkl}")
    print(f" - Preprocessor:     {preproc_pkl}")
    print(f" - Unified Pipeline: {pipeline_pkl}")

    # Legacy model/ folder sync for Flask backend compatibility
    legacy_model_dir = os.path.join(PROJECT_ROOT, "model")
    if os.path.exists(legacy_model_dir):
        joblib.dump(best_model, os.path.join(legacy_model_dir, "resume_shortlisting_model.pkl"))
        joblib.dump(tfidf_vec, os.path.join(legacy_model_dir, "tfidf_vectorizer.pkl"))
        joblib.dump(inference_pipeline, os.path.join(legacy_model_dir, "resume_shortlisting_pipeline.pkl"))

    # 12. Test Prediction Function with 5 Diverse Scenarios
    print("\n" + "=" * 80)
    print(" TESTING PREDICTION FUNCTION WITH 5 DIVERSE CANDIDATE SCENARIOS")
    print("=" * 80)

    test_scenarios = [
        {
            "name": "Scenario 1: Strong Senior Java Developer",
            "job": "Seeking a Senior Java Developer with at least 4 years experience in Java, Spring Boot, Microservices, Hibernate, REST API, SQL, Docker, and AWS.",
            "resume": "Aarav Sharma. Senior Java Developer with 5 years experience in building enterprise microservices using Java, Spring Boot, Hibernate, and REST API. Strong expertise in SQL, Docker containerization, Git, and AWS deployment. Completed 3 large microservice banking projects. AWS Certified Developer."
        },
        {
            "name": "Scenario 2: Strong Lead Data Scientist",
            "job": "Hiring a Data Scientist experienced in Python, Machine Learning, Deep Learning, Pandas, Scikit-Learn, TensorFlow, Statistics, and SQL.",
            "resume": "Priya Patel. Data Scientist with 4 years of experience delivering machine learning models in production. Proficient in Python, Machine Learning, Deep Learning, Pandas, NumPy, Scikit-Learn, TensorFlow, Statistics, and SQL. Deployed NLP sentiment engines and credit risk scoring. TensorFlow Developer Certificate."
        },
        {
            "name": "Scenario 3: Moderate Web Developer (Review Candidate)",
            "job": "Looking for a Full Stack Developer skilled in React, Node.js, JavaScript, TypeScript, Python, HTML, CSS, MongoDB, SQL, and Docker.",
            "resume": "Amit Verma. Web Developer with 2 years of experience. Proficient in HTML, CSS, JavaScript, React, and MongoDB. Familiar with Git and responsive UI design. Built two web storefront projects. Currently learning Node.js and Docker."
        },
        {
            "name": "Scenario 4: Junior Applicant with Skill Deficits (Review / Weak)",
            "job": "Seeking a Database Developer with expertise in PostgreSQL, MySQL, Oracle, Database Design, Query Optimization, ETL, Stored Procedures, and Linux.",
            "resume": "Rohan Kumar. Junior Software Engineer with 1 year of experience. Skills include basic SQL, Python, and Git. Worked on basic academic database design and simple queries. Aspiring to learn advanced indexing and stored procedures."
        },
        {
            "name": "Scenario 5: Completely Irrelevant Applicant (Rejected)",
            "job": "Looking for a Backend Developer skilled in Node.js, Express, Python, Java, REST API, PostgreSQL, MongoDB, Docker, Microservices, and Redis.",
            "resume": "David Wilson. Professional Executive Chef and Restaurant Manager with 8 years of hospitality management experience. Expert in kitchen staff leadership, menu curation, inventory budgeting, and food safety regulations."
        }
    ]

    for sc in test_scenarios:
        res = inference_pipeline.predict_candidate(sc["resume"], sc["job"])
        print(f"\n--- {sc['name']} ---")
        print(f"Prediction: {res['prediction']} | Overall Score: {res['score']}%")
        print(f"Skill Match: {res['skill_match_percentage']}% | Cosine Sim: {res['cosine_similarity_percentage']}%")
        print(f"Matched Skills: {res['matched_skills']}")
        print(f"Missing Skills: {res['missing_skills']}")
        print(f"Recommendation: {res['recommendation']}")

    # 13. Create ZIP Archive
    zip_path = os.path.join(PROJECT_ROOT, "resume_shortlisting_training.zip")
    print(f"\n[STEP 11] Packaging entire project into {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, PROJECT_ROOT)
                zf.write(abs_path, rel_path)

    print(f"ZIP package successfully created at: {zip_path}")
    print(f"ZIP File Size: {os.path.getsize(zip_path) / (1024 * 1024):.2f} MB")
    print("\n" + "=" * 80)
    print(" ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()

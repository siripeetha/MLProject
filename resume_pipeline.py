# -*- coding: utf-8 -*-
"""
ResumeShortlistingPipeline definition for Phase 1 & Phase 2 Flask Integration
"""

import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

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


def clean_nlp_text(text):
    if not isinstance(text, str):
        return ""
    text_lower = text.lower()
    text_clean = re.sub(r"[^a-z0-9+#\.\s]", " ", text_lower)
    tokens = text_clean.split()
    meaningful = [t for t in tokens if t not in NLTK_STOPWORDS and len(t) > 1]
    return " ".join(meaningful)


class ResumeShortlistingPipeline:
    def __init__(self, model, scaler, tfidf_vectorizer, feature_columns, skill_map):
        self.model = model
        self.scaler = scaler
        self.tfidf_vectorizer = tfidf_vectorizer
        self.feature_columns = feature_columns
        self.skill_map = skill_map

    def extract_skills(self, text):
        clean_t = text.lower()
        detected = set()
        for alias, standard in self.skill_map.items():
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, clean_t):
                detected.add(standard)
        return sorted(list(detected))

    def predict_candidate(self, resume_text, job_description):
        # 1. NLP Text Cleaning
        c_res = clean_nlp_text(resume_text)
        c_job = clean_nlp_text(job_description)

        # 2. Skill Extraction
        cand_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        if not job_skills:
            job_skills = ["python", "sql", "git"]

        matched = [s for s in job_skills if s in cand_skills]
        missing = [s for s in job_skills if s not in cand_skills]
        skill_match_score = round((len(matched) / len(job_skills)) * 100.0, 2)

        # 3. TF-IDF Cosine Similarity
        vec_res = self.tfidf_vectorizer.transform([c_res])
        vec_job = self.tfidf_vectorizer.transform([c_job])
        cos_sim = round(float(cosine_similarity(vec_res, vec_job)[0][0]) * 100.0, 2)

        # 4. Experience Parsing
        exp_match = re.search(r"(\d+)\s*\+?\s*years?", resume_text, re.IGNORECASE)
        exp_years = float(exp_match.group(1)) if exp_match else 2.0
        exp_match_score = min(100.0, round((exp_years / 3.0) * 100.0, 2))

        # 5. Education Scoring
        edu_score = 85.0
        if any(deg in resume_text for deg in ["M.Tech", "M.S.", "PhD"]):
            edu_score = 95.0
        elif any(deg in resume_text for deg in ["B.Tech", "B.E.", "MCA"]):
            edu_score = 90.0
        elif any(deg in resume_text for deg in ["BCA", "B.Sc"]):
            edu_score = 80.0

        # 6. Projects & Certifications
        proj_count = len(re.findall(r"(project|platform|engine|dashboard|system)", resume_text, re.IGNORECASE))
        proj_score = min(100.0, max(30.0, proj_count * 25.0))

        cert_count = len(re.findall(r"(certified|certification|aws|azure|oracle)", resume_text, re.IGNORECASE))
        cert_score = 90.0 if cert_count > 0 else 30.0

        # 7. Overall Score Calculation
        overall_score = round(
            (skill_match_score * 0.50) +
            (exp_match_score * 0.20) +
            (edu_score * 0.10) +
            (proj_score * 0.10) +
            (cert_score * 0.10), 2
        )
        overall_score = min(100.0, max(0.0, overall_score))

        # 8. Feature vector
        feat_dict = {
            "experience_years": exp_years,
            "skill_count": len(cand_skills),
            "project_count": proj_count,
            "certification_count": cert_count,
            "skill_match_score": skill_match_score,
            "experience_match_score": exp_match_score,
            "education_match_score": edu_score,
            "project_score": proj_score,
            "certification_score": cert_score,
            "cosine_similarity_score": cos_sim
        }
        df_feat = pd.DataFrame([feat_dict])[self.feature_columns]
        
        # 9. Model prediction
        if self.scaler is not None:
            X_in = self.scaler.transform(df_feat)
        else:
            X_in = df_feat
            
        pred = self.model.predict(X_in)[0]

        # 10. Qualitative Recommendation
        if pred == "SHORTLISTED":
            recommendation = "Strong candidate: High technical alignment, qualified experience, and matching skill profile."
        elif pred == "REVIEW":
            recommendation = "Moderate candidate: Meets foundational requirements with minor skill or experience gaps. Recommend manual review."
        else:
            recommendation = "Unqualified candidate: Significant mismatch in required core skills or requisite experience. Screen out."

        return {
            "prediction": pred,
            "score": overall_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": recommendation
        }

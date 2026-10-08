# -*- coding: utf-8 -*-
"""
Database Service: MongoDB connection and candidate persistence
Zero mock candidates on initial state; strictly dynamic.
"""

import os
import uuid
import datetime
import pandas as pd
from pymongo import MongoClient, DESCENDING

from backend.config import MONGO_URI, DB_NAME, WAREHOUSE_DIR


class DBService:
    def __init__(self):
        self.client = None
        self.db = None
        self.candidates_col = None
        self.jobs_col = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            self.db = self.client[DB_NAME]
            self.candidates_col = self.db["candidates"]
            self.jobs_col = self.db["jobs"]
            print(f"Connected to MongoDB: {DB_NAME}")
            self.seed_jobs_if_needed()
        except Exception as e:
            print(f"MongoDB connection error: {e}")

    def seed_jobs_if_needed(self):
        """Seed job descriptions if jobs collection is empty, so target roles are available."""
        try:
            if self.jobs_col.count_documents({}) == 0:
                dim_job_path = os.path.join(WAREHOUSE_DIR, "dim_job.csv")
                if os.path.exists(dim_job_path):
                    df_jobs = pd.read_csv(dim_job_path)
                    job_docs = []
                    for _, row in df_jobs.iterrows():
                        job_docs.append({
                            "job_id": row["job_id"],
                            "job_role": row["job_role"],
                            "description": row["job_description"],
                            "required_skills": [s.strip() for s in str(row["job_required_skills"]).split(",") if s.strip()],
                            "min_experience": 2 if "Developer" in row["job_role"] else 3,
                            "education": "B.Tech / B.E. / MCA / M.Tech",
                            "location": row.get("location", "Bangalore / Remote"),
                            "created_at": datetime.datetime.utcnow()
                        })
                    if job_docs:
                        self.jobs_col.insert_many(job_docs)
                        print(f"Seeded {len(job_docs)} jobs into MongoDB.")
        except Exception as e:
            print(f"Error seeding jobs: {e}")

    def save_candidate_analysis(self, analysis_result, raw_text=""):
        """
        Stores a newly analyzed candidate into MongoDB.
        Guarantees candidate_name, resume_filename, score, skills, status, and created_at.
        """
        try:
            cand_count = self.candidates_col.count_documents({}) + 1
            cand_id = f"CAND_{cand_count:04d}"
            
            cand_name = analysis_result.get("candidate_name") or analysis_result.get("candidateName") or "Candidate"
            filename = analysis_result.get("resume_filename") or analysis_result.get("resumeFileName") or "resume.pdf"
            sc = round(float(analysis_result.get("score", analysis_result.get("overall_score", 0.0))), 1)
            raw_st = analysis_result.get("status", analysis_result.get("shortlist_status", "Rejected"))
            status = "Selected" if raw_st in ["Selected", "SHORTLISTED"] else "Rejected"

            now = datetime.datetime.utcnow()

            doc = {
                "candidate_id": cand_id,
                "candidate_name": cand_name,
                "candidateName": cand_name,
                "resume_filename": filename,
                "resumeFileName": filename,
                "score": sc,
                "overall_score": sc,
                "status": status,
                "shortlist_status": status,
                "skills": analysis_result.get("skills", []),
                "matched_skills": analysis_result.get("matched_skills", []),
                "missing_skills": analysis_result.get("missing_skills", []),
                "recommendation": analysis_result.get("recommendation", ""),
                "email": analysis_result.get("email", ""),
                "phone": analysis_result.get("phone", ""),
                "education": analysis_result.get("education", ""),
                "experience_years": float(analysis_result.get("experience_years", 0.0)),
                "job_role": analysis_result.get("job_role", "Software Engineer"),
                "skill_match_score": float(analysis_result.get("skill_match_score", 0.0)),
                "experience_match_score": float(analysis_result.get("experience_match_score", 0.0)),
                "education_match_score": float(analysis_result.get("education_match_score", 0.0)),
                "project_score": float(analysis_result.get("project_score", 0.0)),
                "certification_score": float(analysis_result.get("certification_score", 0.0)),
                "cosine_similarity_score": float(analysis_result.get("cosine_similarity_score", 0.0)),
                "raw_text_preview": raw_text[:300] if raw_text else "",
                "created_at": now,
                "createdAt": now.isoformat(),
                "date": now.strftime("%Y-%m-%d %H:%M")
            }
            res = self.candidates_col.insert_one(doc)
            doc["_id"] = str(res.inserted_id)
            doc["created_at"] = now.strftime("%Y-%m-%d %H:%M")
            return doc
        except Exception as e:
            print(f"Error saving candidate to MongoDB: {e}")
            analysis_result["candidate_id"] = f"CAND_ERR_{uuid.uuid4().hex[:6]}"
            return analysis_result

    def get_dashboard_metrics(self):
        """
        Computes summary statistics and candidate scores for live recruitment dashboard.
        Initial state has 0 candidates and empty candidate_scores array.
        Candidate scores are sorted alphabetically by candidate_name for the Dashboard graph.
        """
        try:
            total_cand = self.candidates_col.count_documents({})
            if total_cand == 0:
                return {
                    "total_candidates": 0,
                    "selected_candidates": 0,
                    "rejected_candidates": 0,
                    "average_score": 0.0,
                    "candidate_scores": []
                }

            selected = self.candidates_col.count_documents({
                "$or": [
                    {"status": "Selected"},
                    {"shortlist_status": "Selected"},
                    {"shortlist_status": "SHORTLISTED"}
                ]
            })
            rejected = self.candidates_col.count_documents({
                "$or": [
                    {"status": "Rejected"},
                    {"shortlist_status": "Rejected"},
                    {"shortlist_status": "REJECTED"}
                ]
            })

            # Candidate scores sorted ALPHABETICALLY by candidate_name for Dashboard bar graph
            cursor = self.candidates_col.find({}).sort("candidate_name", 1)
            candidate_scores = []
            total_score = 0.0
            for c in cursor:
                sc = round(float(c.get("score", c.get("overall_score", 0.0))), 1)
                raw_st = c.get("status", c.get("shortlist_status", "Rejected"))
                norm_st = "Selected" if raw_st in ["Selected", "SHORTLISTED"] else "Rejected"
                c_name = c.get("candidate_name") or c.get("candidateName") or "Candidate"
                candidate_scores.append({
                    "candidate_name": c_name,
                    "candidateName": c_name,
                    "score": sc,
                    "status": norm_st
                })
                total_score += sc

            avg_score = round(total_score / total_cand, 1) if total_cand > 0 else 0.0

            return {
                "total_candidates": total_cand,
                "selected_candidates": selected,
                "rejected_candidates": rejected,
                "average_score": avg_score,
                "candidate_scores": candidate_scores
            }
        except Exception as e:
            print(f"Error computing dashboard metrics: {e}")
            return {
                "total_candidates": 0,
                "selected_candidates": 0,
                "rejected_candidates": 0,
                "average_score": 0.0,
                "candidate_scores": []
            }

    def get_candidates(self, search="", status_filter="", role_filter="All", sort_by="score", sort_order="desc", limit=100, skip=0, **kwargs):
        """
        Fetches candidates sorted primarily by score DESC.
        Computes dynamic Rank (1, 2, 3...) for the ranking leaderboard.
        """
        query = {}
        if search:
            query["$or"] = [
                {"candidate_name": {"$regex": search, "$options": "i"}},
                {"candidateName": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"skills": {"$regex": search, "$options": "i"}}
            ]
        if status_filter and status_filter != "All":
            query["$or"] = [
                {"status": status_filter},
                {"shortlist_status": status_filter}
            ]
        if role_filter and role_filter != "All":
            query["job_role"] = role_filter

        cursor = self.candidates_col.find(query).sort([("score", -1), ("overall_score", -1)]).skip(skip).limit(limit)
        candidates = []
        rank = 1 + skip
        for c in cursor:
            c["_id"] = str(c["_id"])
            c["rank"] = rank
            rank += 1

            raw_st = c.get("status", c.get("shortlist_status", "Rejected"))
            c["status"] = "Selected" if raw_st in ["Selected", "SHORTLISTED"] else "Rejected"
            c["score"] = round(float(c.get("score", c.get("overall_score", 0.0))), 1)
            c["candidate_name"] = c.get("candidate_name") or c.get("candidateName") or "Candidate"
            c["resume_filename"] = c.get("resume_filename") or c.get("resumeFileName") or "resume.pdf"

            created = c.get("created_at") or c.get("createdAt")
            if isinstance(created, datetime.datetime):
                c["date"] = created.strftime("%Y-%m-%d %H:%M")
            elif isinstance(created, str):
                c["date"] = created[:16].replace("T", " ")
            else:
                c["date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")

            candidates.append(c)

        total = self.candidates_col.count_documents(query)
        return {"candidates": candidates, "total": total}

    def get_candidate_by_id(self, cand_id):
        cand = self.candidates_col.find_one({"candidate_id": cand_id})
        if cand:
            cand["_id"] = str(cand["_id"])
            if "created_at" in cand and isinstance(cand["created_at"], datetime.datetime):
                cand["created_at"] = cand["created_at"].strftime("%Y-%m-%d %H:%M")
        return cand

    def delete_candidate(self, cand_id):
        res = self.candidates_col.delete_one({"candidate_id": cand_id})
        return res.deleted_count > 0

    def get_jobs(self):
        cursor = self.jobs_col.find().sort("job_id", 1)
        jobs = []
        for j in cursor:
            j["_id"] = str(j["_id"])
            jobs.append(j)
        return jobs

    def create_job(self, job_dict):
        job_dict["created_at"] = datetime.datetime.utcnow()
        res = self.jobs_col.insert_one(job_dict)
        job_dict["_id"] = str(res.inserted_id)
        return job_dict

    def delete_job(self, job_id):
        res = self.jobs_col.delete_one({"job_id": job_id})
        return res.deleted_count > 0


# Singleton database instance
db_service = DBService()

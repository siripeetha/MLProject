# -*- coding: utf-8 -*-
"""
OLAP Service: Implements Multi-Dimensional Roll-up, Drill-down, Slice, and Dice operations
"""

import pandas as pd
from backend.services.warehouse_service import warehouse_service


class OLAPService:
    def __init__(self):
        self.cube = None
        self.build_cube()

    def build_cube(self):
        """Constructs an in-memory multidimensional OLAP cube by joining facts and dimensions."""
        try:
            fact = warehouse_service.data_cache.get("fact_candidate_analysis")
            job = warehouse_service.data_cache.get("dim_job")
            date = warehouse_service.data_cache.get("dim_date")
            exp = warehouse_service.data_cache.get("dim_experience")
            edu = warehouse_service.data_cache.get("dim_education")
            cand = warehouse_service.data_cache.get("dim_candidate")

            if fact is not None and job is not None and date is not None:
                m = fact.merge(job[["job_id", "job_role"]], on="job_id", how="left")
                m = m.merge(date[["date_id", "month", "quarter", "year", "date"]], on="date_id", how="left")
                if exp is not None:
                    m = m.merge(exp[["experience_id", "experience_range"]], on="experience_id", how="left")
                if edu is not None:
                    m = m.merge(edu[["education_id", "degree", "specialization"]], on="education_id", how="left")
                if cand is not None:
                    m = m.merge(cand[["candidate_id", "candidate_name", "location"]], on="candidate_id", how="left")
                self.cube = m
                print(f"OLAP Cube materialized with {len(self.cube)} records.")
        except Exception as e:
            print(f"Error materializing OLAP cube: {e}")

    def rollup(self, hierarchy="quarter"):
        """
        ROLL-UP: Aggregates metrics upwards along the dimensional hierarchy.
        E.g. Month -> Quarter -> Year, or Candidate -> Job Role -> Organization
        """
        if self.cube is None:
            self.build_cube()
        if self.cube is None:
            return []

        if hierarchy == "year":
            group_cols = ["year"]
        elif hierarchy == "quarter":
            group_cols = ["year", "quarter"]
        elif hierarchy == "month":
            group_cols = ["year", "quarter", "month"]
        elif hierarchy == "job_role":
            group_cols = ["job_role"]
        else:
            group_cols = ["year", "quarter"]

        agg = self.cube.groupby(group_cols).agg(
            total_candidates=("candidate_id", "count"),
            avg_overall_score=("overall_score", "mean"),
            avg_skill_match=("skill_match_score", "mean"),
            shortlisted=("shortlist_status", lambda s: (s == "SHORTLISTED").sum()),
            review=("shortlist_status", lambda s: (s == "REVIEW").sum()),
            rejected=("shortlist_status", lambda s: (s == "REJECTED").sum())
        ).reset_index()

        agg["avg_overall_score"] = agg["avg_overall_score"].round(2)
        agg["avg_skill_match"] = agg["avg_skill_match"].round(2)
        agg["shortlist_rate"] = ((agg["shortlisted"] / agg["total_candidates"]) * 100).round(1)

        return agg.to_dict(orient="records")

    def drilldown(self, year=2025, quarter="Q1"):
        """
        DRILL-DOWN: Deconstructs high-level period into detailed monthly/role metrics.
        """
        if self.cube is None:
            self.build_cube()
        if self.cube is None:
            return []

        filtered = self.cube[(self.cube["year"] == int(year)) & (self.cube["quarter"] == str(quarter))]
        agg = filtered.groupby(["month", "job_role"]).agg(
            total_candidates=("candidate_id", "count"),
            avg_overall_score=("overall_score", "mean"),
            shortlisted=("shortlist_status", lambda s: (s == "SHORTLISTED").sum())
        ).reset_index()

        agg["avg_overall_score"] = agg["avg_overall_score"].round(2)
        return agg.sort_values(by=["month", "total_candidates"], ascending=[True, False]).to_dict(orient="records")

    def slice(self, dimension="job_role", value="Java Developer"):
        """
        SLICE: Filters along a single dimension slice.
        """
        if self.cube is None:
            self.build_cube()
        if self.cube is None:
            return {"summary": {}, "records": []}

        if dimension not in self.cube.columns:
            dimension = "job_role"

        filtered = self.cube[self.cube[dimension].astype(str).str.lower() == str(value).lower()]
        
        summary = {
            "dimension": dimension,
            "value": value,
            "total_candidates": len(filtered),
            "avg_overall_score": round(filtered["overall_score"].mean(), 2) if len(filtered) else 0,
            "avg_skill_match": round(filtered["skill_match_score"].mean(), 2) if len(filtered) else 0,
            "shortlisted_count": int((filtered["shortlist_status"] == "SHORTLISTED").sum()),
            "review_count": int((filtered["shortlist_status"] == "REVIEW").sum()),
            "rejected_count": int((filtered["shortlist_status"] == "REJECTED").sum())
        }

        records = filtered[["candidate_id", "candidate_name", "job_role", "experience_range", "overall_score", "shortlist_status"]].head(25).to_dict(orient="records")
        return {"summary": summary, "records": records}

    def dice(self, job_role="Java Developer", experience_range="0-2 years", min_score=70.0):
        """
        DICE: Multi-dimensional sub-cube intersection filter.
        E.g. Job Role = Java Developer AND Experience = 0-2 years AND Overall Score >= 70
        """
        if self.cube is None:
            self.build_cube()
        if self.cube is None:
            return {"criteria": {}, "matched_count": 0, "records": []}

        filtered = self.cube.copy()
        if job_role and job_role != "All":
            filtered = filtered[filtered["job_role"].str.lower() == str(job_role).lower()]
        if experience_range and experience_range != "All":
            filtered = filtered[filtered["experience_range"] == experience_range]
        if min_score is not None:
            filtered = filtered[filtered["overall_score"] >= float(min_score)]

        records = filtered[[
            "candidate_id", "candidate_name", "job_role", "experience_range",
            "skill_match_score", "experience_match_score", "overall_score", "shortlist_status"
        ]].head(30).to_dict(orient="records")

        return {
            "criteria": {
                "job_role": job_role,
                "experience_range": experience_range,
                "min_score": float(min_score)
            },
            "matched_count": len(filtered),
            "records": records
        }


olap_service = OLAPService()

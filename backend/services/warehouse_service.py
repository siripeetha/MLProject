# -*- coding: utf-8 -*-
"""
Data Warehouse Service: Reads and serves Star Schema dimension & fact tables
"""

import os
import pandas as pd
from backend.config import WAREHOUSE_DIR


TABLES_CONFIG = {
    "dim_candidate": {
        "display_name": "Candidate Dimension (DIM_CANDIDATE)",
        "file": "dim_candidate.csv",
        "primary_key": "candidate_id",
        "description": "Stores biographical details, contact info, and aggregate experience."
    },
    "dim_job": {
        "display_name": "Job Dimension (DIM_JOB)",
        "file": "dim_job.csv",
        "primary_key": "job_id",
        "description": "Stores organizational technical positions, descriptions, and mandatory skills."
    },
    "dim_skill": {
        "display_name": "Skill Dimension (DIM_SKILL)",
        "file": "dim_skill.csv",
        "primary_key": "skill_id",
        "description": "Predefined technical skills dictionary grouped into technology domains."
    },
    "dim_date": {
        "display_name": "Date Dimension (DIM_DATE)",
        "file": "dim_date.csv",
        "primary_key": "date_id",
        "description": "Temporal dimension tracking day, month, quarter, and application year."
    },
    "dim_education": {
        "display_name": "Education Dimension (DIM_EDUCATION)",
        "file": "dim_education.csv",
        "primary_key": "education_id",
        "description": "Degree and engineering specialization combinations."
    },
    "dim_experience": {
        "display_name": "Experience Dimension (DIM_EXPERIENCE)",
        "file": "dim_experience.csv",
        "primary_key": "experience_id",
        "description": "Standardized seniority tiers (0-2 yrs, 3-5 yrs, 6-8 yrs, 9+ yrs)."
    },
    "fact_candidate_analysis": {
        "display_name": "Candidate Analysis Fact Table (FACT_CANDIDATE_ANALYSIS)",
        "file": "fact_candidate_analysis.csv",
        "primary_key": ["candidate_id", "job_id", "date_id"],
        "description": "Central fact table storing all numeric metrics and dimensional foreign keys."
    }
}


class WarehouseService:
    def __init__(self):
        self.data_cache = {}
        self.load_tables()

    def load_tables(self):
        for key, conf in TABLES_CONFIG.items():
            fpath = os.path.join(WAREHOUSE_DIR, conf["file"])
            if os.path.exists(fpath):
                try:
                    df = pd.read_csv(fpath)
                    self.data_cache[key] = df
                    print(f"Loaded Warehouse table: {key} ({len(df)} rows)")
                except Exception as e:
                    print(f"Error loading {conf['file']}: {e}")

    def get_overview(self):
        """Returns metadata for all warehouse tables."""
        tables = []
        for key, conf in TABLES_CONFIG.items():
            df = self.data_cache.get(key)
            row_count = len(df) if df is not None else 0
            cols = list(df.columns) if df is not None else []
            tables.append({
                "table_key": key,
                "display_name": conf["display_name"],
                "primary_key": conf["primary_key"],
                "description": conf["description"],
                "rows": row_count,
                "columns": cols
            })

        star_schema_info = {
            "fact_table": "FACT_CANDIDATE_ANALYSIS",
            "dimensions": [
                {"name": "DIM_CANDIDATE", "join_key": "candidate_id"},
                {"name": "DIM_JOB", "join_key": "job_id"},
                {"name": "DIM_SKILL", "join_key": "skill_id"},
                {"name": "DIM_DATE", "join_key": "date_id"},
                {"name": "DIM_EDUCATION", "join_key": "education_id"},
                {"name": "DIM_EXPERIENCE", "join_key": "experience_id"}
            ]
        }
        return {"tables": tables, "schema": star_schema_info}

    def get_table_data(self, table_key, search="", page=1, limit=20, sort_col="", sort_dir="asc"):
        """Paginates and filters a given warehouse table."""
        df = self.data_cache.get(table_key)
        if df is None:
            return {"rows": [], "total": 0, "page": page, "columns": []}

        filtered = df.copy()
        if search:
            mask = filtered.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)
            filtered = filtered[mask]

        if sort_col and sort_col in filtered.columns:
            ascending = (sort_dir.lower() != "desc")
            filtered = filtered.sort_values(by=sort_col, ascending=ascending)

        total = len(filtered)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = filtered.iloc[start_idx:end_idx]

        # Convert NaN to None for JSON serialization
        rows = paginated_df.where(pd.notnull(paginated_df), None).to_dict(orient="records")
        return {
            "table_key": table_key,
            "columns": list(df.columns),
            "rows": rows,
            "total": total,
            "page": page,
            "limit": limit
        }


warehouse_service = WarehouseService()

# -*- coding: utf-8 -*-
"""
Application Configuration for Resume Shortlisting & Candidate Analytics Backend
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Server Settings
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "resume_shortlisting_db"

# Storage Directories
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODELS_DIR = os.path.join(BASE_DIR, "models")
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data_warehouse")
REPORTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "resume_shortlisting_project", "reports")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "resume_shortlisting_project", "data")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

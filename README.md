# 📄 Resume Screening and Candidate Analytics System
### *AI-Powered Resume Screening using Data Mining & Machine Learning*

An end-to-end, integrated recruitment screening platform that connects your **Google Colab Data Mining & ML pipeline** directly to a **Flask backend**, **MongoDB database**, and modern **React web application**.

---

## 🌟 The 3 Main Core Features

1. **Dashboard (Home Page)**
   - **Initial State:** When opened with an empty database:
     - Total Candidates = `0`
     - Selected Candidates = `0`
     - Rejected Candidates = `0`
     - Average Score = `0`
     - Bar Graph is **Empty** with the message *"No Candidate Data - Upload a resume in the Resume Analyzer to see live scores"*
     - **No fake or mock candidates**
   - **Dynamic Updates:** Whenever a resume is analyzed:
     - Counters increment dynamically.
     - Candidate appears in the bar graph with their score.
     - Graph X-axis is sorted **alphabetically by candidate name**.
     - Color-coded: **Selected** (Green) vs **Rejected** (Red).

2. **Resume Analyzer**
   - Upload candidate resume PDF (also supports DOCX and TXT).
   - Target Job Role selection and job description matching.
   - Extracts resume text, parses contact info, and tokenizes NLP content.
   - TF-IDF Cosine Similarity & exact Colab Machine Learning model evaluation.
   - Outputs:
     - **Candidate Name**
     - **Resume Score** (e.g. `86 / 100`)
     - **Status**: `Selected` or `Rejected`
     - **Extracted Skills**
     - **Relevant / Matched Skills**
     - **Missing Skills**
     - **Selection Recommendation**
   - Automatically stores the candidate permanently in MongoDB.

3. **Candidate Ranking**
   - **Initial State:** Shows *"No candidates analyzed yet"* when the database is empty.
   - **Dynamic Ranking:** Displays all analyzed candidates dynamically from the database.
   - Columns:
     - **Rank** (`#1`, `#2`, `#3`... sorted primarily by score descending)
     - **Candidate Name**
     - **Score** (`/ 100`)
     - **Status** (`Selected` / `Rejected`)
     - **Resume** (Filename)
     - **Date** (Timestamp)
   - Real-time search filter and candidate inspection modal.

---

## ⚡ Quick Start: How to Run the Website

### Option 1: One-Click Startup (Windows)
Double-click `start_system.bat` in the project root:
```powershell
.\start_system.bat
```
This automatically starts:
- Flask Backend Server on [http://127.0.0.1:5000](http://127.0.0.1:5000)
- React Vite Frontend on [http://localhost:3000](http://localhost:3000)
- Opens your default web browser to the application.

---

### Option 2: Manual Terminal Startup

#### Terminal 1 — Flask Backend
```powershell
cd c:\Users\Sirip\Downloads\MLProject
.\venv\Scripts\activate
python backend/app.py
```

#### Terminal 2 — React Frontend
```powershell
cd c:\Users\Sirip\Downloads\MLProject\frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

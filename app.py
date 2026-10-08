"""
==============================================================================
Resume Mining and Classification System - Flask Web Backend
==============================================================================
Full-stack backend providing:
- Web homepage (GET /)
- Resume analysis & ML classification API (POST /predict)
- Data Mining training metrics API (GET /metrics)
- Server health check API (GET /health)
==============================================================================
"""

import os
import sys
import re
import json
import uuid
import shutil
import numpy as np
import joblib

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pypdf import PdfReader

# OCR & Image Processing
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    OCR_SUPPORTED = True
except ImportError:
    OCR_SUPPORTED = False

# Import text preprocessing from training module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from training.preprocess import clean_resume_text, configure_tesseract, STOPWORDS


# ==============================================================================
# 1. Flask App Initialization & Configuration
# ==============================================================================

app = Flask(
    __name__,
    static_folder='assets',
    static_url_path='/assets',
    template_folder='templates'
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MODEL_FOLDER = os.path.join(BASE_DIR, 'model')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')

# Model artifact paths
MODEL_PATH = os.path.join(MODEL_FOLDER, 'resume_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_FOLDER, 'tfidf_vectorizer.pkl')
ENCODER_PATH = os.path.join(MODEL_FOLDER, 'label_encoder.pkl')
METRICS_PATH = os.path.join(MODEL_FOLDER, 'metrics.json')

# Constraints
MAX_FILE_SIZE_MB = 16
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# Initialize Tesseract configuration
configure_tesseract()


# ==============================================================================
# 2. Model Loading (Cached at Startup / Hot-Reloaded)
# ==============================================================================

loaded_model = None
loaded_vectorizer = None
loaded_encoder = None


def load_ml_artifacts():
    """Loads trained model, TF-IDF vectorizer, and label encoder from model/ directory."""
    global loaded_model, loaded_vectorizer, loaded_encoder

    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH) and os.path.exists(ENCODER_PATH):
        try:
            loaded_model = joblib.load(MODEL_PATH)
            loaded_vectorizer = joblib.load(VECTORIZER_PATH)
            loaded_encoder = joblib.load(ENCODER_PATH)
            print("[INFO] Successfully loaded trained ML model and TF-IDF vectorizer from model/")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model files from model/: {e}")
            return False
    return False

# Attempt initial load
load_ml_artifacts()


# ==============================================================================
# 3. Skills Extraction Taxonomy (Easily Extendable)
# ==============================================================================

COMMON_SKILLS_LIST = [
    # Programming Languages
    "Python", "Java", "C", "C++", "C#", "SQL", "HTML", "CSS", "JavaScript",
    "TypeScript", "PHP", "Ruby", "Go", "Rust", "R", "MATLAB", "Scala", "Bash",
    # Frameworks & Web
    "React", "Node.js", "Express", "Angular", "Vue", "Django", "Flask",
    "FastAPI", "Spring Boot", "REST API", "GraphQL", "MongoDB", "PostgreSQL", "MySQL",
    # Data Mining, AI & Analytics
    "Machine Learning", "Deep Learning", "Data Science", "Data Analysis",
    "Data Mining", "Natural Language Processing", "NLP", "Computer Vision",
    "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras",
    # Tools, Cloud & Business Intelligence
    "Excel", "Power BI", "Tableau", "AWS", "Azure", "GCP", "Docker",
    "Kubernetes", "Git", "GitHub", "JIRA", "Linux", "CI/CD",
    # Soft & Management Skills
    "Communication", "Leadership", "Project Management", "Problem Solving",
    "Teamwork", "Agile", "Scrum", "Critical Thinking", "Collaboration"
]


def extract_skills_from_text(raw_text: str) -> list[str]:
    """
    Scans resume text for common technical & professional skills using regex word boundaries.
    """
    if not raw_text:
        return []

    detected_skills = []
    for skill in COMMON_SKILLS_LIST:
        # Match whole word boundaries (case-insensitive)
        escaped = re.escape(skill)
        pattern = rf'(?<!\w){escaped}(?!\w)'
        if re.search(pattern, raw_text, re.IGNORECASE):
            detected_skills.append(skill)

    # Deduplicate while preserving order
    return list(dict.fromkeys(detected_skills))


def extract_resume_info(raw_text: str) -> dict:
    """
    Mines email, phone, links, and general summary indicators.
    """
    # 1. Emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = list(dict.fromkeys(re.findall(email_pattern, raw_text)))

    # 2. Phone numbers
    phone_pattern = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
    raw_phones = re.findall(phone_pattern, raw_text)
    phones = [p.strip() for p in raw_phones if 9 <= len(re.sub(r'\D', '', p)) <= 15]
    phones = list(dict.fromkeys(phones))

    # 3. Links
    link_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:github\.com|linkedin\.com\/in|kaggle\.com|gitlab\.com)[^\s,]+'
    links = list(dict.fromkeys(re.findall(link_pattern, raw_text, re.IGNORECASE)))

    # 4. Summary preview (first non-empty 350 characters cleaned)
    first_lines = [line.strip() for line in raw_text.split('\n') if len(line.strip()) > 3]
    summary_snippet = " ".join(first_lines[:4]) if first_lines else "Summary unavailable."
    if len(summary_snippet) > 350:
        summary_snippet = summary_snippet[:350].rsplit(' ', 1)[0] + '...'

    return {
        "emails": emails[:3],
        "phones": phones[:2],
        "links": links[:4],
        "summary": summary_snippet
    }


# ==============================================================================
# 4. Hybrid Text Extraction (Digital PDF + OCR Fallback)
# ==============================================================================

def extract_pdf_content(pdf_path: str) -> tuple[str, int]:
    """
    Extracts text from PDF:
    - First attempts digital extraction with pypdf (instant).
    - If digital extraction yields < 50 characters (e.g. scanned image PDF),
      uses pdf2image + pytesseract OCR.
    """
    extracted_text = ""
    pages_count = 1

    # 1. Digital text extraction attempt
    try:
        reader = PdfReader(pdf_path)
        pages_count = max(1, len(reader.pages))
        digital_chunks = [page.extract_text() or "" for page in reader.pages]
        digital_text = "\n".join(digital_chunks).strip()
        if len(digital_text) >= 60:
            return digital_text, pages_count
    except Exception:
        pass

    # 2. Scanned PDF fallback via OCR
    if not OCR_SUPPORTED:
        raise RuntimeError("PDF is an image/scanned document, but OCR libraries (pdf2image/pytesseract) are unavailable.")

    try:
        # Convert pages to images at 150 DPI
        images = convert_from_path(pdf_path, dpi=150)
        pages_count = len(images)
        ocr_chunks = []

        for img in images:
            page_text = pytesseract.image_to_string(img)
            if page_text:
                ocr_chunks.append(page_text)
            img.close()

        extracted_text = "\n".join(ocr_chunks).strip()
        return extracted_text, pages_count

    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {str(e)}")


# ==============================================================================
# 5. Prediction Pipeline
# ==============================================================================

def classify_resume(cleaned_text: str, raw_text: str) -> dict:
    """
    Predicts category using trained ML model if available.
    If model is not yet trained, provides a clear transparent placeholder.
    """
    global loaded_model, loaded_vectorizer, loaded_encoder

    # Check/reload model if newly trained
    if loaded_model is None:
        load_ml_artifacts()

    # If real trained model is available:
    if loaded_model is not None and loaded_vectorizer is not None and loaded_encoder is not None:
        try:
            # 1. TF-IDF vectorization
            text_vec = loaded_vectorizer.transform([cleaned_text])
            # 2. Classification
            pred_idx = loaded_model.predict(text_vec)[0]
            predicted_category = loaded_encoder.inverse_transform([pred_idx])[0]

            # 3. Confidence score (if model supports predict_proba)
            confidence_score = None
            if hasattr(loaded_model, "predict_proba"):
                try:
                    probs = loaded_model.predict_proba(text_vec)[0]
                    confidence_score = round(float(np.max(probs)) * 100, 2)
                except Exception:
                    confidence_score = None

            return {
                "category": str(predicted_category),
                "confidence": confidence_score,
                "is_model_trained": True,
                "message": "Classified using your trained Data Mining model."
            }
        except Exception as e:
            print(f"[ERROR] Inference failed with trained model: {e}")

    # Fallback when model is not yet placed in model/
    # (Transparent rule-based baseline so the web application can be tested immediately)
    lower_raw = raw_text.lower()
    keyword_map = {
        "Data Science & Analytics": ["python", "machine learning", "data science", "sql", "pandas", "tableau", "ai", "deep learning"],
        "Software Engineering": ["developer", "software", "java", "c++", "javascript", "backend", "frontend", "api"],
        "Cloud & DevOps": ["aws", "azure", "docker", "kubernetes", "cloud", "linux", "ci/cd", "devops"],
        "Web Development": ["html", "css", "react", "node.js", "frontend", "mongodb", "javascript", "web"],
        "Human Resources": ["recruitment", "hr", "sourcing", "talent", "interviews", "onboarding"],
        "Finance & Banking": ["accounting", "finance", "audit", "tax", "banking", "financial analysis"]
    }

    scores = {}
    for cat, kws in keyword_map.items():
        scores[cat] = sum(1 for kw in kws if kw in lower_raw)

    best_cat, max_s = max(scores.items(), key=lambda x: x[1])
    if max_s == 0:
        best_cat = "General Professional"

    return {
        "category": best_cat,
        "confidence": None,
        "is_model_trained": False,
        "message": "Standby Baseline: Model training files (resume_model.pkl, tfidf_vectorizer.pkl, label_encoder.pkl) are pending in model/ folder."
    }


# ==============================================================================
# 6. HTTP Routes
# ==============================================================================

@app.route('/')
def home():
    """Renders the main full-stack user interface."""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint returning server and model status."""
    return jsonify({
        "status": "healthy",
        "ocr_available": OCR_SUPPORTED,
        "model_loaded": loaded_model is not None,
        "artifacts_detected": os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)
    })


@app.route('/metrics', methods=['GET'])
def metrics():
    """Returns training evaluation metrics from model/metrics.json if trained."""
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"available": True, "metrics": data})
        except Exception as e:
            return jsonify({"available": False, "error": str(e)})

    return jsonify({
        "available": False,
        "message": "Model has not been trained yet. Run 'python training/train_model.py' to generate metrics."
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts resume PDF upload, runs OCR / text extraction, cleans text,
    extracts skills & contacts, runs ML classification, and returns JSON.
    """
    # 1. Validation: check file presence
    if 'resume_pdf' not in request.files:
        return jsonify({
            "success": False,
            "error": "No resume file uploaded. Please select a PDF file."
        }), 400

    file = request.files['resume_pdf']

    if not file or file.filename.strip() == '':
        return jsonify({
            "success": False,
            "error": "No file selected. Please choose a valid resume PDF."
        }), 400

    # Validate extension
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({
            "success": False,
            "error": "Invalid file format. Only PDF files (.pdf) are supported."
        }), 400

    # 2. Save file temporarily in uploads/
    temp_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    try:
        file.save(temp_filepath)

        # 3. Extract text (digital or OCR)
        raw_text, page_count = extract_pdf_content(temp_filepath)

        if not raw_text or len(raw_text.strip()) < 15:
            return jsonify({
                "success": False,
                "error": "Unable to extract text from the PDF. The file may be empty or contain unreadable scanned images."
            }), 400

        # 4. Text Preprocessing & Cleaning
        cleaned_text = clean_resume_text(raw_text)

        # 5. Extract Skills & Candidate Information
        extracted_skills = extract_skills_from_text(raw_text)
        info = extract_resume_info(raw_text)

        # 6. ML Classification Prediction
        prediction_result = classify_resume(cleaned_text, raw_text)

        # Word count & metrics
        word_count = len(raw_text.split())

        return jsonify({
            "success": True,
            "filename": filename,
            "page_count": page_count,
            "word_count": word_count,
            "prediction": prediction_result,
            "extracted_skills": extracted_skills,
            "candidate_info": info,
            "raw_text_preview": raw_text[:3500]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error analyzing resume: {str(e)}"
        }), 500

    finally:
        # Disk hygiene: remove temporary PDF
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass


# ==============================================================================
# 7. Server Main Entrypoint
# ==============================================================================

if __name__ == '__main__':
    print("\n" + "="*65)
    print(" 🚀 RESUME MINING AND CLASSIFICATION SYSTEM")
    print(" 🌐 Access application at: http://127.0.0.1:5000")
    print("="*65 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)

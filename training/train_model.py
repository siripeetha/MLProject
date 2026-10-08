"""
==============================================================================
Resume Mining and Classification System - Model Training Pipeline
==============================================================================
Loads the processed resume dataset (data/resume_dataset.csv), extracts TF-IDF
features, trains and evaluates classification models:
- Multinomial Naive Bayes (Fast, classic text classification benchmark)
- Logistic Regression (Linear probabilistic classifier)
- Linear SVM (Maximum-margin linear classifier)
Evaluates metrics, generates confusion matrix, and saves artifacts:
- model/resume_model.pkl
- model/tfidf_vectorizer.pkl
- model/label_encoder.pkl
- model/metrics.json
- assets/confusion_matrix.png
==============================================================================
"""

import os
import sys
import json
import argparse
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

# Optional classifiers (handles OS / DLL policy differences smoothly)
try:
    from sklearn.linear_model import LogisticRegression
    LOGISTIC_AVAILABLE = True
except Exception:
    LOGISTIC_AVAILABLE = False

try:
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    SVM_AVAILABLE = True
except Exception:
    SVM_AVAILABLE = False

# Optional visualization
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ==============================================================================
# 1. Training & Evaluation Pipeline
# ==============================================================================

def train_and_evaluate(
    data_path: str = "data/resume_dataset.csv",
    model_dir: str = "model",
    test_size: float = 0.2,
    random_state: int = 42
):
    """
    Main training workflow for Resume Category Classification.
    """
    print("\n" + "="*70)
    print(" RESUME MINING SYSTEM - MACHINE LEARNING TRAINING PIPELINE")
    print("="*70)

    # 1. Load Dataset
    if not os.path.exists(data_path):
        print(f"\n[ERROR] Dataset not found at: {data_path}")
        print("Please run 'python training/preprocess.py' first to extract OCR text,")
        print("or provide your processed resume CSV dataset.")
        return False

    print(f"\n[1/6] Loading processed dataset from: {data_path}")
    df = pd.read_csv(data_path)

    # Validate required columns
    required_cols = {"category", "resume_text"}
    if not required_cols.issubset(df.columns):
        print(f"[ERROR] CSV must contain columns: {required_cols}. Found: {df.columns.tolist()}")
        return False

    # Drop nulls or empty texts
    initial_count = len(df)
    df = df.dropna(subset=['category', 'resume_text'])
    df = df[df['resume_text'].str.strip().str.len() > 20]
    clean_count = len(df)

    print(f"      Total records loaded: {initial_count} (Clean valid records: {clean_count})")
    categories = sorted(df['category'].unique())
    num_categories = len(categories)
    print(f"      Detected {num_categories} unique categories:")
    for cat in categories[:10]:
        print(f"        - {cat} ({sum(df['category'] == cat)} samples)")
    if num_categories > 10:
        print(f"        ... and {num_categories - 10} more categories.")

    # 2. Encode Labels
    print("\n[2/6] Encoding target category labels...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['category'])
    X = df['resume_text']

    # 3. Train / Test Split
    print(f"\n[3/6] Splitting dataset ({int((1-test_size)*100)}% Train / {int(test_size*100)}% Test)...")
    stratify = y if min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    print(f"      Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

    # 4. TF-IDF Feature Extraction
    print("\n[4/6] Extracting TF-IDF features (unigrams + bigrams, max 5,000 features)...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words='english'
    )
    X_train_vec = tfidf.fit_transform(X_train)
    X_test_vec = tfidf.transform(X_test)
    print(f"      TF-IDF feature matrix shape: {X_train_vec.shape}")

    # 5. Model Training & Comparison
    print("\n[5/6] Training and comparing candidate classification algorithms...")
    candidates = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1)
    }

    if LOGISTIC_AVAILABLE:
        candidates["Logistic Regression"] = LogisticRegression(max_iter=1000, C=1.0, random_state=random_state)

    if SVM_AVAILABLE:
        candidates["Linear SVM (Calibrated)"] = CalibratedClassifierCV(
            LinearSVC(C=1.0, random_state=random_state, dual='auto'),
            cv=3
        )

    best_model_name = None
    best_model = None
    best_acc = -1.0
    results_summary = {}

    for name, model in candidates.items():
        print(f"      Fitting {name}...")
        model.fit(X_train_vec, y_train)
        pred_test = model.predict(X_test_vec)
        acc = accuracy_score(y_test, pred_test)
        results_summary[name] = acc
        print(f"      -> {name} Test Accuracy: {acc * 100:.2f}%")

        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_model = model

    print(f"\n      Selected Best Model: {best_model_name} (Accuracy: {best_acc * 100:.2f}%)")

    # 6. Evaluation Metrics & Reports
    print("\n[6/6] Computing comprehensive evaluation metrics...")
    y_train_pred = best_model.predict(X_train_vec)
    y_test_pred = best_model.predict(X_test_vec)

    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='weighted', zero_division=0)

    clf_report_text = classification_report(y_test, y_test_pred, target_names=label_encoder.classes_, zero_division=0)
    conf_mat = confusion_matrix(y_test, y_test_pred)

    print("\n" + "-"*60)
    print(" CLASSIFICATION EVALUATION REPORT")
    print("-"*60)
    print(clf_report_text)
    print(f" Training Accuracy: {train_acc * 100:.2f}%")
    print(f" Testing Accuracy:  {test_acc * 100:.2f}%")
    print(f" Weighted Precision:{precision * 100:.2f}%")
    print(f" Weighted Recall:   {recall * 100:.2f}%")
    print(f" Weighted F1-Score: {f1 * 100:.2f}%")
    print("-"*60)

    # 7. Save Model Artifacts
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs("assets", exist_ok=True)

    model_path = os.path.join(model_dir, "resume_model.pkl")
    vec_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    le_path = os.path.join(model_dir, "label_encoder.pkl")
    metrics_path = os.path.join(model_dir, "metrics.json")
    cm_image_path = os.path.join("assets", "confusion_matrix.png")

    joblib.dump(best_model, model_path)
    joblib.dump(tfidf, vec_path)
    joblib.dump(label_encoder, le_path)

    metrics_payload = {
        "status": "trained",
        "total_resumes": clean_count,
        "num_categories": num_categories,
        "categories": list(label_encoder.classes_),
        "best_model": best_model_name,
        "train_accuracy": round(float(train_acc) * 100, 2),
        "test_accuracy": round(float(test_acc) * 100, 2),
        "precision": round(float(precision) * 100, 2),
        "recall": round(float(recall) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "candidate_comparisons": {k: round(v * 100, 2) for k, v in results_summary.items()},
        "has_confusion_matrix_image": False
    }

    # Generate Confusion Matrix Chart
    if MATPLOTLIB_AVAILABLE and num_categories <= 35:
        try:
            plt.figure(figsize=(10, 8))
            plt.imshow(conf_mat, interpolation='nearest', cmap=plt.cm.Blues)
            plt.title(f'Confusion Matrix - {best_model_name}', fontsize=14, pad=15)
            plt.colorbar()
            tick_marks = np.arange(len(label_encoder.classes_))
            plt.xticks(tick_marks, label_encoder.classes_, rotation=90, fontsize=8)
            plt.yticks(tick_marks, label_encoder.classes_, fontsize=8)
            plt.tight_layout()
            plt.ylabel('True Category')
            plt.xlabel('Predicted Category')
            plt.savefig(cm_image_path, dpi=200, bbox_inches='tight')
            plt.close()
            metrics_payload["has_confusion_matrix_image"] = True
            print(f" [SAVED] Confusion matrix plot saved to: {cm_image_path}")
        except Exception as e:
            print(f" [WARNING] Could not plot confusion matrix: {e}")

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\n [SAVED] Trained Model:       {model_path}")
    print(f" [SAVED] TF-IDF Vectorizer:   {vec_path}")
    print(f" [SAVED] Label Encoder:       {le_path}")
    print(f" [SAVED] Evaluation Metrics:  {metrics_path}")
    print("="*70)
    print(" Training completed successfully! The Flask web application")
    print(" will now automatically load and use these trained model files.")
    print("="*70 + "\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Mining System - ML Model Training")
    parser.add_argument("--data", default="data/resume_dataset.csv", help="Path to processed CSV dataset")
    parser.add_argument("--model-dir", default="model", help="Directory to save model artifacts")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio (default: 0.2)")

    args = parser.parse_args()
    train_and_evaluate(
        data_path=args.data,
        model_dir=args.model_dir,
        test_size=args.test_size
    )

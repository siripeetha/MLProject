"""
==============================================================================
Resume Mining and Classification System - Model Evaluation Script
==============================================================================
Standalone script to evaluate trained model artifacts on test datasets,
display detailed classification reports, confusion matrix, or test sample texts.
==============================================================================
"""

import os
import sys
import argparse
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

# Set path root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from training.preprocess import clean_resume_text


def evaluate_existing_model(
    model_path: str = "model/resume_model.pkl",
    vec_path: str = "model/tfidf_vectorizer.pkl",
    le_path: str = "model/label_encoder.pkl",
    data_path: str = "data/resume_dataset.csv"
):
    """
    Evaluates saved model files against a test dataset.
    """
    print("\n" + "="*65)
    print(" 🔍 RESUME CLASSIFICATION MODEL EVALUATION")
    print("="*65)

    # 1. Verify model files exist
    for p in [model_path, vec_path, le_path]:
        if not os.path.exists(p):
            print(f"[ERROR] Required model artifact not found: {p}")
            print("Please run 'python training/train_model.py' first.")
            return

    # 2. Load artifacts
    print("[1/3] Loading saved model artifacts...")
    model = joblib.load(model_path)
    tfidf = joblib.load(vec_path)
    label_encoder = joblib.load(le_path)
    print(f"      Model type:    {type(model).__name__}")
    print(f"      Vocabulary:    {len(tfidf.vocabulary_)} features")
    print(f"      Classes ({len(label_encoder.classes_)}): {list(label_encoder.classes_[:5])}...")

    # 3. Load Dataset
    if not os.path.exists(data_path):
        print(f"\n[INFO] Dataset {data_path} not found. Skipping full dataset evaluation.")
        return

    print(f"\n[2/3] Evaluating on dataset: {data_path}")
    df = pd.read_csv(data_path).dropna(subset=['category', 'resume_text'])

    # Transform
    X_vec = tfidf.transform(df['resume_text'])
    y_true = label_encoder.transform(df['category'])
    y_pred = model.predict(X_vec)

    # Metrics
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

    print("\n[3/3] Results:")
    print("-" * 55)
    print(f" Total Samples Evaluated: {len(df)}")
    print(f" Accuracy:                {acc * 100:.2f}%")
    print(f" Weighted Precision:      {prec * 100:.2f}%")
    print(f" Weighted Recall:         {rec * 100:.2f}%")
    print(f" Weighted F1-Score:       {f1 * 100:.2f}%")
    print("-" * 55)

    print("\nFull Classification Report:")
    print(classification_report(y_true, y_pred, target_names=label_encoder.classes_, zero_division=0))
    print("="*65 + "\n")


def test_sample_text(text: str, model_path="model/resume_model.pkl", vec_path="model/tfidf_vectorizer.pkl", le_path="model/label_encoder.pkl"):
    """
    Tests prediction on a specific raw text snippet.
    """
    if not os.path.exists(model_path):
        print(f"[ERROR] Model file not found: {model_path}")
        return

    model = joblib.load(model_path)
    tfidf = joblib.load(vec_path)
    label_encoder = joblib.load(le_path)

    cleaned = clean_resume_text(text)
    vec = tfidf.transform([cleaned])
    pred_idx = model.predict(vec)[0]
    category = label_encoder.inverse_transform([pred_idx])[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(vec)[0]
        confidence = float(np.max(probs))

    print(f"\nPredicted Category: {category}")
    if confidence is not None:
        print(f"Confidence Score:   {confidence * 100:.2f}%\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Trained Resume Mining Model")
    parser.add_argument("--model", default="model/resume_model.pkl")
    parser.add_argument("--vectorizer", default="model/tfidf_vectorizer.pkl")
    parser.add_argument("--encoder", default="model/label_encoder.pkl")
    parser.add_argument("--data", default="data/resume_dataset.csv")
    parser.add_argument("--sample-text", default=None, help="Optional text string to classify directly")

    args = parser.parse_args()
    if args.sample_text:
        test_sample_text(args.sample_text, args.model, args.vectorizer, args.encoder)
    else:
        evaluate_existing_model(args.model, args.vectorizer, args.encoder, args.data)

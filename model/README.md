# 🤖 Model Directory

Place your trained Machine Learning / Data Mining model and vectorizer files here once you finish training in Google Colab.

---

## 📁 Expected Files

| File | Description | Required? |
|------|-------------|-----------|
| `resume_classifier.pkl` | Your trained classifier (e.g., MultinomialNB, SVM, Random Forest, Logistic Regression) | **Yes** (when trained) |
| `tfidf_vectorizer.pkl` | Your fitted TF-IDF vectorizer (or CountVectorizer) | **Yes** (when trained) |

---

## 🚀 How to Export from Google Colab

At the end of your training notebook in Google Colab, run:

```python
import joblib

# 1. Save your fitted TF-IDF vectorizer
joblib.dump(tfidf, 'tfidf_vectorizer.pkl')

# 2. Save your trained classification model
joblib.dump(classifier_model, 'resume_classifier.pkl')

# 3. Download the files to your computer
from google.colab import files
files.download('tfidf_vectorizer.pkl')
files.download('resume_classifier.pkl')
```

---

## 🔌 Connecting to this Application

1. Move the downloaded `resume_classifier.pkl` and `tfidf_vectorizer.pkl` files into this `model/` folder.
2. Restart the Flask app (`py app.py` or `python app.py`).
3. The app will automatically detect the files and switch from the **"Placeholder Baseline"** to your **actual trained Data Mining model**!

---

*Note: While these files are absent, the application runs a transparent keyword baseline so you can test the frontend, PDF parsing, skill extraction, and UI.*

"""
==============================================================================
Resume Mining and Classification System - Preprocessing & OCR Pipeline
==============================================================================
Batch OCR text extraction & cleaning pipeline for the 8,905 Resume dataset.
- Converts image-based PDF pages to images using pdf2image (DPI=150)
- Extracts text via Tesseract OCR (with pypdf quick-check)
- Cleans and normalizes resume text (lowercase, regex, stopwords)
- Saves progress periodically to data/resume_dataset.csv
- Supports resuming from checkpoints (skips already processed PDFs)
- Gracefully handles corrupted PDFs without halting
==============================================================================
"""

import os
import sys
import re
import argparse
import shutil
import pandas as pd
from PIL import Image

# Import PDF extraction libraries
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# ==============================================================================
# 1. OCR Configuration & Tesseract Setup (Windows & Linux Friendly)
# ==============================================================================

def configure_tesseract(custom_path=None):
    """
    Locates and configures the Tesseract OCR executable.
    Checks user path, environment variables, and standard Windows install paths.
    """
    if not PYTESSERACT_AVAILABLE:
        print("[WARNING] pytesseract is not installed.")
        return False

    candidates = [
        custom_path,
        os.environ.get("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        shutil.which("tesseract")
    ]

    for path in candidates:
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    # If tesseract command is in PATH
    if shutil.which("tesseract"):
        return True

    return False


# Standard English Stopwords list (no large external downloads required)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}


# ==============================================================================
# 2. Text Preprocessing Function
# ==============================================================================

def clean_resume_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Cleans raw resume text for Data Mining and Machine Learning:
    - Converts to lowercase
    - Removes URLs and email addresses
    - Removes special symbols & punctuation while preserving alphanumeric words
    - Removes single letters and digits
    - Removes English stopwords
    - Normalizes extra whitespaces
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Lowercase
    cleaned = text.lower()

    # 2. Remove URLs and emails
    cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', cleaned)
    cleaned = re.sub(r'\S+@\S+', ' ', cleaned)

    # 3. Remove non-alphabetical symbols (keep alphanumeric and spaces)
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', cleaned)

    # 4. Tokenize and filter stopwords
    words = cleaned.split()
    if remove_stopwords:
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    else:
        words = [w for w in words if len(w) > 1]

    # 5. Join with single spaces
    return " ".join(words).strip()


# ==============================================================================
# 3. Single PDF OCR & Extraction
# ==============================================================================

def extract_text_with_ocr(pdf_path: str, dpi: int = 150, poppler_path: str = None) -> str:
    """
    Extracts text from a single PDF:
    1. First tries digital text extraction via pypdf (instant).
    2. If text is empty or < 50 chars (scanned image PDF), converts pages to
       images at given DPI (150) and extracts text page-by-page via Tesseract OCR.
    """
    # Quick check: digital PDF text extraction
    if PYPDF_AVAILABLE:
        try:
            reader = PdfReader(pdf_path)
            extracted = "".join([page.extract_text() or "" for page in reader.pages]).strip()
            if len(extracted) >= 60:
                return extracted
        except Exception:
            pass  # Fall through to OCR

    # OCR extraction: page-by-page processing (avoids loading all images at once)
    if not PDF2IMAGE_AVAILABLE or not PYTESSERACT_AVAILABLE:
        raise RuntimeError("pdf2image and pytesseract are required for OCR extraction.")

    try:
        # Convert pages to images
        kwargs = {"dpi": dpi}
        if poppler_path and os.path.exists(poppler_path):
            kwargs["poppler_path"] = poppler_path

        images = convert_from_path(pdf_path, **kwargs)
        extracted_text_chunks = []

        for page_idx, img in enumerate(images):
            # OCR each page image
            page_text = pytesseract.image_to_string(img)
            if page_text:
                extracted_text_chunks.append(page_text)
            # Free image memory immediately
            img.close()

        del images
        return "\n".join(extracted_text_chunks).strip()

    except Exception as e:
        raise RuntimeError(f"OCR failed for {os.path.basename(pdf_path)}: {str(e)}")


# ==============================================================================
# 4. Batch Dataset Processor with Checkpoints
# ==============================================================================

def process_dataset(
    dataset_dir: str,
    output_csv: str = "data/resume_dataset.csv",
    batch_size: int = 25,
    dpi: int = 150,
    tesseract_cmd: str = None,
    poppler_path: str = None
):
    """
    Scans dataset_dir (folders = categories), processes all PDFs with OCR & cleaning,
    and appends them to output_csv periodically. Skips already processed files.
    """
    configure_tesseract(tesseract_cmd)

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)

    # 1. Check existing progress
    processed_filenames = set()
    if os.path.exists(output_csv):
        try:
            existing_df = pd.read_csv(output_csv)
            if 'filename' in existing_df.columns:
                processed_filenames = set(existing_df['filename'].dropna().astype(str).tolist())
                print(f"[RESUME] Found existing {output_csv} with {len(processed_filenames)} resumes already processed.")
        except Exception as e:
            print(f"[WARNING] Could not read existing {output_csv}: {e}")

    # 2. Discover all PDF files across category subfolders
    all_pdf_tasks = []
    if not os.path.exists(dataset_dir):
        print(f"[ERROR] Dataset directory not found: {dataset_dir}")
        print("Please place your Kaggle dataset in data/Resumes PDF/ or specify --data-dir.")
        return

    for root, dirs, files in os.walk(dataset_dir):
        category = os.path.basename(root)
        # Skip root directory itself if it's the parent
        if os.path.abspath(root) == os.path.abspath(dataset_dir):
            continue

        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                all_pdf_tasks.append((file, category, full_path))

    total_files = len(all_pdf_tasks)
    if total_files == 0:
        print(f"[INFO] No PDF files found in {dataset_dir}. Check dataset folder structure.")
        return

    print(f"\n[INFO] Found {total_files} total PDF resumes across categories.")
    remaining_tasks = [t for t in all_pdf_tasks if t[0] not in processed_filenames]
    print(f"[INFO] Resumes left to process: {len(remaining_tasks)} / {total_files}\n")

    if not remaining_tasks:
        print("[SUCCESS] All resumes have already been processed into CSV!")
        return

    # 3. Process remaining files in batches
    batch_records = []
    success_count = len(processed_filenames)
    error_count = 0

    for idx, (filename, category, filepath) in enumerate(remaining_tasks, 1):
        try:
            # OCR Extraction
            raw_text = extract_text_with_ocr(filepath, dpi=dpi, poppler_path=poppler_path)
            # Text Cleaning
            cleaned_text = clean_resume_text(raw_text)

            if len(cleaned_text) < 15:
                print(f"[{idx}/{len(remaining_tasks)}] ⚠️ {filename} ({category}) -> Empty / minimal text extracted.")
            else:
                batch_records.append({
                    "filename": filename,
                    "category": category,
                    "resume_text": cleaned_text
                })
                success_count += 1
                print(f"[{idx}/{len(remaining_tasks)}] ✅ {filename} ({category}) -> {len(cleaned_text.split())} words")

        except Exception as err:
            error_count += 1
            print(f"[{idx}/{len(remaining_tasks)}] ❌ {filename} ({category}) -> ERROR: {err}")

        # Checkpoint: Save progress every batch_size resumes or on final file
        if len(batch_records) >= batch_size or (idx == len(remaining_tasks) and batch_records):
            batch_df = pd.DataFrame(batch_records)
            write_header = not os.path.exists(output_csv) or os.stat(output_csv).st_size == 0
            batch_df.to_csv(output_csv, mode='a', header=write_header, index=False)
            print(f"[CHECKPOINT] Saved batch of {len(batch_records)} resumes to {output_csv}. Total saved: {success_count}")
            batch_records.clear()

    print("\n" + "="*60)
    print(f" 🎉 OCR & PREPROCESSING COMPLETE!")
    print(f" Total Successfully Processed: {success_count} / {total_files}")
    print(f" Total Errors Encountered:     {error_count}")
    print(f" Processed Dataset Saved To:   {output_csv}")
    print("="*60 + "\n")


# ==============================================================================
# 5. CLI Entrypoint
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Mining System - Batch OCR & Preprocessing")
    parser.add_argument("--data-dir", default="data/Resumes PDF", help="Path to folder containing category folders of PDFs")
    parser.add_argument("--output", default="data/resume_dataset.csv", help="Path for output CSV")
    parser.add_argument("--batch-size", type=int, default=25, help="Batch size for periodic saving")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for PDF to image conversion (default: 150)")
    parser.add_argument("--tesseract-cmd", default=None, help="Custom path to tesseract.exe")
    parser.add_argument("--poppler-path", default=None, help="Custom path to poppler/bin")

    args = parser.parse_args()
    process_dataset(
        dataset_dir=args.data_dir,
        output_csv=args.output,
        batch_size=args.batch_size,
        dpi=args.dpi,
        tesseract_cmd=args.tesseract_cmd,
        poppler_path=args.poppler_path
    )

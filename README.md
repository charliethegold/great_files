# Free Batch OCR Tool for Legal Document Processing

**TL;DR:** A free, open-source desktop app that does batch OCR on thousands of images/PDFs with progress tracking, pause/resume, and smart skip for already-processed files. Built for legal professionals dealing with large document collections in discovery, FOIA requests, and case preparation.

---

## Background

Legal practice regularly involves processing thousands of scanned pages — court filings, discovery documents, deposition exhibits, FOIA responses, and more. Commercial OCR services are expensive at scale, and existing free tools either crash on large batches or lack basic features like pause/resume.

This tool was built using Python and Tesseract OCR to handle exactly that workflow.

---

## Features

✅ **Batch Processing** - Handles hundreds/thousands of files automatically, including subdirectories

✅ **Dark Mode UI** - Easy on the eyes for long processing sessions (5+ hours)

✅ **Progress Tracking** 
   - Real-time progress bar with percentage
   - File counter (processed/remaining)
   - Live time tracking (elapsed + estimated remaining)

✅ **Pause & Resume** - Stop processing anytime, resume later without losing progress

✅ **Smart Skip** - Automatically skips already-processed files (crucial if you need to restart)

✅ **Detailed Logging** - Scrolling list of completed files with processing time

✅ **Multi-Format Support** - JPG, PNG, PDF, TIFF, and more

---

## Why This Matters for Legal Practice

Large document productions are common in litigation. At 2–5 seconds per file, a 2,000-page document set takes several hours. This tool gives you:
- A way to pause/resume (crashes happen, hearings happen)
- Skip already-processed files (don't waste hours reprocessing after a restart)
- Visual progress (sanity check for overnight runs)
- Everything runs locally — no client data leaves your machine

---

## Technical Details

**Stack:**
- Python 3.x
- Tesseract OCR (free, open-source)
- Tkinter (GUI)
- PIL/Pillow (image processing)
- pdf2image (PDF handling)

**System Requirements:**
- Mac, Windows, or Linux
- Python 3.6+
- Tesseract OCR installed

**Processing Speed:**
- ~2 seconds per image
- ~5 seconds per PDF page
- Varies based on image quality and hardware

---

## Installation

1. Install Python from python.org
2. Install Tesseract OCR:
   - **Mac:** `brew install tesseract`
   - **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux:** `sudo apt install tesseract-ocr`

3. Install Python dependencies:
   ```bash
   pip install pytesseract pillow pdf2image
   ```

4. Download the script: `legal_ocr.py`

5. Run:
   ```bash
   python3 legal_ocr.py
   ```

---

## Usage

1. **Select Folder** - Choose the folder containing your scanned documents
2. **Click Start** - The app scans all files (including subfolders) and estimates time
3. **Monitor Progress** - Watch the progress bar, file counter, and time estimates
4. **Pause if Needed** - Stop for a hearing, resume later
5. **Results** - Text files appear in `ocr_results` folder with the same filenames

---

## Legal Use Cases

- **Discovery** - Make scanned production sets fully searchable before review
- **FOIA requests** - Process government document dumps efficiently
- **Case preparation** - Convert deposition exhibits and court filings to searchable text
- **Due diligence** - Rapidly process large document sets in transactional matters
- **Public records** - Search and analyze public court documents and filings
- **Accessibility** - Make scanned documents screen-reader friendly for clients

---

## Future Improvements (Maybe)

- [ ] Language selection for non-English documents
- [ ] Batch processing multiple folders in queue
- [ ] OCR quality settings (speed vs accuracy)
- [ ] Export to searchable PDF instead of just text
- [ ] Bates number detection and indexing

---

## Download

[GitHub link would go here if hosted]

**License:** MIT (do whatever you want with it)

---

## Privacy Note

Everything runs locally on your machine. No documents are uploaded to external servers. This is important for attorney-client privilege and client confidentiality — your files never leave your machine.

---

**Q: Tesseract accuracy?**
A: Very good for printed text such as court filings and typed legal documents. Handwriting is hit-or-miss.

**Q: Can it handle [specific format]?**
A: Currently supports common image formats (JPG, PNG, TIFF) and PDFs. Open an issue if you need additional formats.

**Q: Processing speed?**
A: Depends on your CPU and image quality. M1 Mac processes ~30 files/minute. Older hardware may be slower.

# I Built a Free Batch OCR Tool to Process the Epstein Files (and Any Large Document Collection)

**TL;DR:** Created a free, open-source desktop app that does batch OCR on thousands of images/PDFs with progress tracking, pause/resume, and smart skip for already-processed files. Perfect for the recent Epstein document releases or any large archive.

---

## Background

With the recent release of Epstein-related documents by Congress, I needed a way to OCR thousands of scanned pages to make them searchable. Commercial OCR services would cost a fortune for this volume, and existing free tools either crashed on large batches or lacked basic features like pause/resume.

So I built this tool using Python and Tesseract OCR.

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

## Why I Built This

The Epstein files are ~2,800+ scanned documents. At ~2-5 seconds per file, that's 5.5 hours of processing. I needed:
- A way to pause/resume (crashes happen, life happens)
- Skip already-processed files (don't waste hours reprocessing)
- Visual progress (sanity check for overnight runs)
- Free and open-source (transparency matters)

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
- Your mileage may vary based on image quality and hardware

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

4. Download the script: `epstein_ocr_final.py`

5. Run:
   ```bash
   python3 epstein_ocr_final.py
   ```

---

## Usage

1. **Select Folder** - Choose the folder containing your images/PDFs
2. **Click Start** - The app scans all files (including subfolders) and estimates time
3. **Monitor Progress** - Watch the progress bar, file counter, and time estimates
4. **Pause if Needed** - Stop for coffee, resume later
5. **Results** - Text files appear in `ocr_results` folder with the same filenames

---

## Use Cases Beyond Epstein Files

This tool is useful for anyone dealing with large document collections:

- **FOIA requests** - Government document dumps
- **Legal discovery** - Scanned court documents
- **Academic research** - Historical archives, old newspapers
- **Personal projects** - Digitizing family photos with text, old letters
- **Accessibility** - Making scanned documents searchable and screen-reader friendly

---

## Screenshots

[Dark mode interface with progress tracking]
[File list showing completed OCR results]
[Time estimation display]

---

## Future Improvements (Maybe)

- [ ] Language selection for non-English documents
- [ ] Batch processing multiple folders in queue
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] OCR quality settings (speed vs accuracy)
- [ ] Export to searchable PDF instead of just text

Let me know if there's interest!

---

## Download

[GitHub link would go here if hosted]

**License:** MIT (do whatever you want with it)

---

## Final Thoughts

Public transparency depends on accessible documents. If documents are locked in scanned images, they're not truly public. OCR is a small step toward making information truly searchable and analyzable.

Hope this helps someone else working through large document releases!

---

**Edit:** Holy inbox! Thanks for the interest. A few common questions:

**Q: Why not use [commercial service]?**
A: For 2,800 files, commercial OCR would cost $50-500 depending on the service. This is free and runs locally (privacy bonus).

**Q: Tesseract accuracy?**
A: Surprisingly good for printed text. Handwriting is hit-or-miss. For official documents like court filings, it's excellent.

**Q: Can it handle [specific format]?**
A: Currently supports common image formats (JPG, PNG, TIFF) and PDFs. If there's demand, I can add more formats.

**Q: Processing speed?**
A: Depends on your CPU and image quality. M1 Mac processes ~30 files/minute. Older hardware may be slower.

**Q: Is my data safe?**
A: Everything runs locally on your machine. Nothing uploaded to the cloud. You can read the code - it's ~400 lines of Python.

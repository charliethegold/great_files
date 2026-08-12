#!/usr/bin/env python3
"""
Re-OCR low-confidence pages using Claude's vision model.

Reads the flagged_for_review.txt file written by epstein_ocr_final.py and
re-transcribes just those files through the Claude API, which typically
does much better than Tesseract on poor scans, handwriting, stamps, and
unusual layouts.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-...
    python3 claude_reocr.py /path/to/folder

The folder should be the same one you selected in the OCR app (the one
containing ocr_results/flagged_for_review.txt). Original Tesseract output
for reprocessed files is preserved alongside as *.tesseract.txt.
"""

import base64
import io
import os
import sys
import time
from pathlib import Path

import anthropic
from PIL import Image
from pdf2image import convert_from_path

MODEL = os.environ.get("CLAUDE_OCR_MODEL", "claude-haiku-4-5-20251001")
PROMPT = (
    "Transcribe all text visible in this document image exactly as it "
    "appears, including headers, footers, stamps, and handwritten "
    "annotations. Output only the transcribed text, with no commentary, "
    "preamble, or markdown formatting. If a section is illegible, mark it "
    "as [illegible] rather than guessing."
)


def image_to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def load_flagged(flagged_path):
    entries = []
    with open(flagged_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t", 1)
            entries.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return entries


def transcribe_image(client, img):
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_to_base64(img),
                    },
                },
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def reprocess_file(client, source):
    if source.suffix.lower() == ".pdf":
        pages = convert_from_path(source)
        parts = [f"\n--- Page {i} ---\n{transcribe_image(client, page)}"
                  for i, page in enumerate(pages, 1)]
        return "".join(parts)
    return transcribe_image(client, Image.open(source))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 claude_reocr.py /path/to/folder")
        sys.exit(1)

    folder = Path(sys.argv[1])
    output_folder = folder / "ocr_results"
    flagged_path = output_folder / "flagged_for_review.txt"
    if not flagged_path.exists():
        print(f"No flagged file found at {flagged_path}")
        print("Run epstein_ocr_final.py on this folder first.")
        sys.exit(1)

    entries = load_flagged(flagged_path)
    if not entries:
        print("No flagged files to reprocess.")
        return

    print(f"Found {len(entries)} flagged files to re-OCR with Claude ({MODEL})")
    client = anthropic.Anthropic()

    for idx, (path_str, reason) in enumerate(entries, 1):
        source = Path(path_str)
        print(f"[{idx}/{len(entries)}] {source.name} (flagged: {reason})")

        if not source.exists():
            print("    skip: source file no longer exists")
            continue

        output_file = output_folder / f"{source.stem}.txt"
        backup_file = output_folder / f"{source.stem}.tesseract.txt"

        for attempt in (1, 2):
            try:
                text = reprocess_file(client, source)
                if output_file.exists() and not backup_file.exists():
                    output_file.rename(backup_file)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"    done ({len(text)} chars)")
                break
            except anthropic.RateLimitError:
                if attempt == 2:
                    print("    failed: still rate limited after retry")
                    break
                print("    rate limited, waiting 30s and retrying...")
                time.sleep(30)
            except Exception as e:
                print(f"    error: {e}")
                break

        time.sleep(1)  # be polite to the API

    print("\nDone. Original Tesseract output preserved as *.tesseract.txt for comparison.")


if __name__ == "__main__":
    main()

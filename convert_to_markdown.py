#!/usr/bin/env python3
"""Convert a file to Markdown (.md). Called by the macOS Quick Action."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


PANDOC_FORMATS = {
    ".docx": "docx",
    ".doc": "docx",
    ".odt": "odt",
    ".rtf": "rtf",
    ".html": "html",
    ".htm": "html",
    ".epub": "epub",
    ".tex": "latex",
    ".org": "org",
    ".rst": "rst",
    ".textile": "textile",
    ".mediawiki": "mediawiki",
}

PLAIN_TEXT = {".txt", ".log", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml", ".ini", ".conf"}

IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".webp"}


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def unique_path(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix, parent = target.stem, target.suffix, target.parent
    i = 2
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def write_md(target: Path, body: str) -> Path:
    out = unique_path(target)
    out.write_text(body, encoding="utf-8")
    return out


def convert_with_pandoc(src: Path, fmt: str, out: Path) -> Path:
    out = unique_path(out)
    subprocess.run(
        ["pandoc", "--from", fmt, "--to", "gfm", "--wrap=none",
         "--output", str(out), str(src)],
        check=True,
    )
    return out


def convert_pdf(src: Path, out: Path) -> Path:
    if have("pandoc"):
        try:
            return convert_with_pandoc(src, "pdf", out)
        except subprocess.CalledProcessError:
            pass
    if have("pdftotext"):
        out = unique_path(out)
        subprocess.run(["pdftotext", "-layout", str(src), str(out)], check=True)
        return out
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError(
            "No PDF tool found. Install one of: pandoc, poppler (pdftotext), or `pip install pypdf`."
        )
    reader = PdfReader(str(src))
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        chunks.append(f"\n\n<!-- page {i} -->\n\n{page.extract_text() or ''}")
    return write_md(out, "".join(chunks).strip() + "\n")


def convert_image(src: Path, out: Path) -> Path:
    if not have("tesseract"):
        raise RuntimeError("Install tesseract for image OCR: `brew install tesseract`.")
    result = subprocess.run(
        ["tesseract", str(src), "-", "-l", "eng"],
        capture_output=True, text=True, check=True,
    )
    body = f"# {src.stem}\n\n{result.stdout.strip()}\n"
    return write_md(out, body)


def convert(src: Path) -> Path:
    if not src.exists():
        raise FileNotFoundError(src)

    ext = src.suffix.lower()
    out = src.with_suffix(".md")

    if ext == ".md":
        target = src.with_name(f"{src.stem} (copy).md")
        shutil.copy2(src, unique_path(target))
        return target

    if ext in PLAIN_TEXT:
        body = src.read_text(encoding="utf-8", errors="replace")
        return write_md(out, body)

    if ext in PANDOC_FORMATS:
        if not have("pandoc"):
            raise RuntimeError(f"Install pandoc to convert {ext}: `brew install pandoc`.")
        return convert_with_pandoc(src, PANDOC_FORMATS[ext], out)

    if ext == ".pdf":
        return convert_pdf(src, out)

    if ext in IMAGE_FORMATS:
        return convert_image(src, out)

    # Fallback: try pandoc autodetect, otherwise treat as plain text.
    if have("pandoc"):
        try:
            return convert_with_pandoc(src, "markdown", out)  # let pandoc guess
        except subprocess.CalledProcessError:
            pass
    body = src.read_text(encoding="utf-8", errors="replace")
    return write_md(out, body)


def notify(title: str, message: str) -> None:
    if not have("osascript"):
        return
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], check=False)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: convert_to_markdown.py <file> [<file> ...]", file=sys.stderr)
        return 2

    failures = []
    outputs = []
    for arg in argv[1:]:
        src = Path(arg).expanduser().resolve()
        try:
            out = convert(src)
            outputs.append(out)
            print(f"OK  {src} -> {out}")
        except Exception as exc:
            failures.append((src, exc))
            print(f"ERR {src}: {exc}", file=sys.stderr)

    if outputs:
        if len(outputs) == 1:
            notify("Markdown", f"Created {outputs[0].name}")
        else:
            notify("Markdown", f"Created {len(outputs)} files")
    if failures:
        names = ", ".join(p.name for p, _ in failures)
        notify("Markdown — failed", names)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

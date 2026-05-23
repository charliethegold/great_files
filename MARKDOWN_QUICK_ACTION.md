# Convert to Markdown — macOS Right-Click Quick Action

Right-click any file in Finder and convert it to Markdown (`.md`).
Output is written next to the original file.

## Supported formats

| Type                                       | Engine                    |
| ------------------------------------------ | ------------------------- |
| `.txt .csv .tsv .json .xml .yaml .ini`     | direct copy with `.md`    |
| `.docx .doc .odt .rtf .html .epub .tex`    | `pandoc`                  |
| `.pdf`                                     | `pandoc` → `pdftotext` → `pypdf` |
| `.jpg .png .tif .bmp .gif .webp`           | `tesseract` OCR           |

## Install

```bash
# 1. (Optional) install conversion engines
brew install pandoc poppler tesseract

# 2. Run the installer
./install_quick_action.sh
```

The installer:
1. Copies `convert_to_markdown.py` to `~/.local/share/convert-to-markdown/`
2. Generates a `.workflow` bundle at `~/Library/Services/Convert to Markdown.workflow`
3. Reloads the macOS Services registry

## Use

1. Right-click a file in Finder.
2. Choose **Quick Actions → Convert to Markdown** (may be nested under **Services**).
3. A `.md` file appears next to the original. A notification confirms success.

If the action doesn't appear:
- Open **System Settings → Keyboard → Keyboard Shortcuts → Services**.
- Under "Files and Folders", tick **Convert to Markdown**.

## Uninstall

```bash
rm -rf "$HOME/Library/Services/Convert to Markdown.workflow"
rm -rf "$HOME/.local/share/convert-to-markdown"
/System/Library/CoreServices/pbs -update
```

## CLI usage

The Python script also works standalone:

```bash
python3 convert_to_markdown.py document.docx report.pdf scan.png
```

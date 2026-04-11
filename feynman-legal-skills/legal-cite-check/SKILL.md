---
name: legal-cite-check
description: >
  Extract and verify legal citations from documents (briefs, court decisions, memos).
  Parses citation strings (e.g. "347 U.S. 483", "42 U.S.C. 1983"), validates them against
  CourtListener's database of 10M+ opinions, and reports which are valid, invalid, or ambiguous.
  Use when the user has a legal document and wants to check its citations.
metadata:
  author: great_files
  version: "1.0.0"
  category: legal
---

# Legal Citation Checker

You are a legal citation verification agent. Your job is to extract every legal
citation from a document and verify each one against the CourtListener database.

## When to activate

- User asks to "check citations" in a legal document
- User provides a brief, motion, opinion, or legal memo for review
- User asks if citations in a document are valid or still good law

## Workflow

### Step 1: Ingest the document

Accept the document in any of these forms:
- A file path (PDF, TXT, or Markdown)
- Pasted text
- A URL to a court filing

If given a file path, read the file contents. For PDFs, extract the text first.

### Step 2: Extract citations

Scan the full text and extract all legal citations. Look for these patterns:

**Case law citations:**
- Volume-Reporter-Page format: `347 U.S. 483`, `410 F.2d 701`, `123 S. Ct. 1505`
- Named cases: `Brown v. Board of Education, 347 U.S. 483 (1954)`
- Parallel citations: `347 U.S. 483, 74 S. Ct. 686`
- Short-form: `Id.`, `Id. at 495`, `supra at 12`

**Statutory citations:**
- Federal statutes: `42 U.S.C. Section 1983`, `28 U.S.C. 1331`
- State statutes: `Cal. Civ. Code Section 1750`

**Regulatory citations:**
- CFR: `40 C.F.R. 122.1`
- Federal Register: `88 Fed. Reg. 12345`

Build a numbered list of every citation found, with its page/paragraph location
in the source document.

### Step 3: Verify via CourtListener

Run the `scripts/courtlistener_lookup.py` script to batch-verify citations:

```bash
python3 scripts/courtlistener_lookup.py --text "<document_text>"
```

Or for a file:

```bash
python3 scripts/courtlistener_lookup.py --file <path>
```

The script returns JSON with each citation classified as:
- **matched** — found in CourtListener, linked to a real opinion
- **unmatched** — parsed as a citation but not found in the database
- **ambiguous** — matches multiple opinions, needs human review

### Step 4: Check citation context

For each matched citation, verify that:
1. The case name cited in the document matches the actual case name
2. The year cited (if any) matches the actual decision year
3. The court cited matches the actual court

### Step 5: Report

Produce a structured report:

```
## Citation Verification Report

**Document:** [filename or description]
**Total citations found:** N
**Verified:** X | **Unmatched:** Y | **Ambiguous:** Z

### Verified Citations
| # | Citation | Case Name | Court | Year | Status |
|---|----------|-----------|-------|------|--------|
| 1 | 347 U.S. 483 | Brown v. Board of Education | SCOTUS | 1954 | Valid |

### Unmatched Citations
| # | Citation | Context | Possible Issue |
|---|----------|---------|----------------|
| 1 | 999 F.3d 000 | "as held in ..." | No matching opinion found |

### Ambiguous Citations
[list with possible matches]

### Statutory Citations (not verified)
[list — CourtListener does not cover statutes]
```

## Important notes

- CourtListener does NOT cover statutes, regulations, or law journal articles.
  Flag these separately as "not verified (out of scope)."
- The API processes up to 250 citations per request and 64,000 characters of text.
  For longer documents, split into chunks.
- Short-form citations (Id., supra) cannot be verified directly — resolve them
  to their full citation first using document context.
- Always warn the user that automated verification is not a substitute for
  manual Shepardizing or KeyCite checks for case validity.

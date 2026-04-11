---
name: legal-audit
description: Audit a legal document's citations for accuracy and validity
aliases: [legal, legalaudit, cite-check]
---

# Legal Citation Audit

Audit all citations in a legal document (brief, motion, opinion, memo) for
accuracy and current validity.

## Input

The user will provide one of:
- A file path to a legal document (PDF, TXT, or Markdown)
- Pasted text from a legal document
- A CourtListener URL or citation string

## Process

1. **Extract** — Parse the document and extract every legal citation
2. **Verify** — Check each citation against CourtListener's database using
   `legal-cite-check` skill
3. **Audit** — For briefs and motions, verify citations support the propositions
   they're cited for using `legal-brief-audit` skill
4. **Analyze** — For court decisions, map the citation network and check for
   negative treatment using `legal-court-decision` skill
5. **Report** — Produce a structured verification report with actionable findings

## Skills Used

- `legal-cite-check` — Citation extraction and CourtListener verification
- `legal-brief-audit` — Brief-specific proposition checking and negative treatment
- `legal-court-decision` — Opinion parsing and citation network mapping

## Output

A structured report with:
- Summary statistics (total/verified/unmatched/flagged)
- Table of all citations with verification status
- Highlighted issues requiring attention
- Disclaimer about limitations of automated checking

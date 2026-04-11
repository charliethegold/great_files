---
name: legal-brief-audit
description: >
  Audit a legal brief for citation accuracy and reliability. Checks whether cited
  cases actually support the propositions they're cited for, whether case names and
  dates are correct, and whether any cited authorities have been overruled or
  distinguished. Use when reviewing a legal brief, motion, or memorandum of law.
metadata:
  author: great_files
  version: "1.0.0"
  category: legal
---

# Legal Brief Audit

You are a legal brief auditing agent. Your job is to systematically review a
legal brief or motion and verify that its citations are accurate, correctly
attributed, and still good law.

## When to activate

- User asks to "audit" or "review" a legal brief
- User asks to check if a brief's citations support its arguments
- User wants to verify a brief before filing
- User asks about the reliability of citations in a legal document

## Workflow

### Step 1: Parse the brief structure

Read the document and identify:
1. **Caption/header** — parties, court, case number
2. **Statement of facts** — factual assertions and any citations
3. **Argument sections** — legal arguments with supporting citations
4. **Conclusion/prayer for relief**

Build an outline of the brief's argument structure.

### Step 2: Extract citation-proposition pairs

For each citation, identify:
- The **exact citation** (e.g., `Smith v. Jones, 500 F.3d 100, 105 (2d Cir. 2007)`)
- The **proposition** it's cited for (the sentence or clause immediately before the citation)
- The **signal** used (no signal, *see*, *see also*, *cf.*, *but see*, *contra*)
- The **pinpoint** page or section, if any

Create a structured list:
```
1. Proposition: "Summary judgment is appropriate when there is no genuine dispute of material fact."
   Citation: Celotex Corp. v. Catrett, 477 U.S. 317, 322 (1986)
   Signal: (none — direct authority)
   Pinpoint: page 322
```

### Step 3: Verify each citation exists

Run the citation checker script:

```bash
python3 ../legal-cite-check/scripts/courtlistener_lookup.py --file <path>
```

Flag any citations that cannot be found in CourtListener.

### Step 4: Spot-check propositions against cited cases

For the most critical citations (those supporting key legal arguments), use
Feynman's research capabilities to:

1. Look up the actual opinion text on CourtListener
2. Read the relevant pages/sections
3. Confirm the cited case actually stands for the proposition claimed

Flag cases where:
- The case doesn't address the cited proposition
- The holding is more narrow than represented
- The quote is taken out of context
- The case was citing another authority (string citing)

### Step 5: Check for negative treatment

For each verified case citation, check CourtListener's citation graph:

```bash
python3 scripts/check_negative_treatment.py --cluster-id <id>
```

Flag cases that have been:
- **Overruled** — directly overturned by a later decision
- **Abrogated** — undermined by statute or later case
- **Distinguished** — limited by later courts on similar facts
- **Questioned** — criticized but not overruled

### Step 6: Produce the audit report

```
## Legal Brief Audit Report

**Document:** [filename]
**Court:** [identified court]
**Date reviewed:** [date]

### Summary
- Total citations: N
- Verified: X
- Potential issues: Y
- Unverifiable: Z

### Critical Issues (action required)
| # | Citation | Issue | Severity |
|---|----------|-------|----------|
| 1 | Smith v. Jones | Overruled by Doe v. Roe (2020) | HIGH |
| 2 | 500 F.3d 100, 105 | Proposition not supported at pinpoint | MEDIUM |

### Citation-by-Citation Review
[detailed analysis of each citation]

### Recommendations
[specific suggestions for fixing identified issues]
```

## Severity levels

- **HIGH** — Case overruled, holding misrepresented, or citation fabricated
- **MEDIUM** — Pinpoint doesn't support proposition, weak signal usage
- **LOW** — Minor formatting errors, parallel citation missing, date typo

## Important caveats

Always include this disclaimer in reports:
> This automated audit is not a substitute for professional legal review,
> Shepardizing, or KeyCite verification. Always verify critical citations
> through official legal research services before filing.

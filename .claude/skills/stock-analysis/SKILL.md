---
name: stock-analysis
description: Research and produce a structured analysis of a publicly-traded stock by ticker (e.g. NOK, AAPL, MSFT). Use when the user asks for an opinion, "take", evaluation, breakdown, outlook, or due-diligence on a stock, ETF, or other publicly-listed equity. Pulls recent price/news/fundamentals via web research and returns fundamentals, technicals, sentiment, risks, and a clearly-labeled non-advisory bottom line.
---

# Stock Analysis Skill

Produce a structured, sourced evaluation of a publicly-traded equity. This is **research and education only** — never financial advice.

## When to use

Trigger on requests like:
- "What's your take on NOK / TSLA / etc."
- "Should I look at <ticker>?"
- "Analyze / evaluate / break down <company> stock"
- "Bull and bear case for <ticker>"

## Required inputs

- **Ticker** (or company name — resolve to the primary listed ticker).
- If the user gave only a name, confirm the exchange/ticker before deep research (e.g. Nokia → NOK on NYSE, NOKIA on Helsinki).

## Workflow

1. **Gather data with WebSearch + WebFetch.** Always pull *current-year* information — prices and narratives go stale fast.
   - Recent price action and 52-week range
   - Latest quarterly earnings (revenue, EPS, guidance, surprise vs. consensus)
   - Key headlines from the last ~3 months (M&A, contracts, regulatory, leadership)
   - Analyst consensus (rating, average target) — note that targets are opinions, not predictions
   - Sector context and 1–2 closest comparables
2. **Do not fabricate numbers.** If a figure isn't in the search results, say "not found in this pass" rather than guessing. Round and cite the source.
3. **Write the report** using the template below. Keep it scannable.

## Output template

```
# <TICKER> — <Company Name>
_As of <date> · price ~<last close> (<exchange>)_

## Snapshot
- Market cap, sector, primary business lines (1–2 lines)
- 52-week range and YTD performance

## Fundamentals
- Revenue trend (last 2–3 years + most recent quarter)
- Profitability: gross margin, operating margin, net income, FCF
- Balance sheet: cash vs. debt, dividend (yield + payout if any)
- Valuation: P/E (trailing + forward if available), EV/EBITDA, P/S — vs. sector

## Recent catalysts (last ~90 days)
- Bullet list of material news with dates and 1-line "why it matters"

## Technicals (light)
- Trend vs. 50/200-day MA, notable support/resistance, volume notes
- Flag clearly that technicals are pattern-based, not predictive

## Bull case
- 3–5 bullets

## Bear case
- 3–5 bullets

## Key risks
- Company-specific, sector, macro, regulatory

## Bottom line
- 2–4 sentence synthesis: who this stock might suit (e.g. "income-oriented investors comfortable with telecom-equipment cyclicality") and what to watch next (next earnings date, key contract decision, etc.)
- **End every report with this exact disclaimer:**
  > Not financial advice. This is informational research generated from public sources and may be incomplete or out of date. Do your own due diligence and consider speaking with a licensed advisor before investing.
```

## Style rules

- **Cite sources** as markdown links at the bottom under `Sources:` (WebSearch already requires this).
- **Date-stamp the report** so the user knows when the data was pulled.
- **No price predictions, no buy/sell calls.** Frame as "considerations," "what bulls argue," "what bears argue."
- **Flag uncertainty.** If consensus is split or data is stale, say so.
- **Keep it tight.** Aim for ~400–700 words total unless the user asks for depth.

## Anti-patterns (do not do)

- Inventing P/E ratios, revenue figures, or analyst targets.
- Saying "this stock will go up" or "you should buy."
- Skipping the disclaimer.
- Using stale (>6 month) data without flagging it.

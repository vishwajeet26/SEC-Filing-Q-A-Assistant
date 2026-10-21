# Client Brief — Driftwood Capital

## Who they are

Driftwood Capital is an independent investment research firm. They sell deep equity research to institutional clients — hedge funds, mutual funds, pension funds — on a subscription basis. Revenue depends on the quality and speed of their analysts' insight.

## The problem

Every analyst covers a set of public companies. Each of those companies publishes annual reports (10-Ks) and quarterly reports (10-Qs) with the SEC — hundreds of pages of numbers, tables, and narrative per filing, per company, per year.

- Analysts spend roughly **half of every week** on source-document intake: scanning filings, hunting for the sections they care about, copy-pasting into manual notes, comparing year over year.
- Only after that intake work can they produce original analysis — the part clients actually pay for.
- The process is repetitive, error-prone, and lives in analysts' personal files. It is the single biggest drag on research output.
- Portfolio managers at client funds don't have the bandwidth to read every filing either — they depend on Driftwood doing it for them.

## What they want

An internal chatbot — a **document copilot** — where analysts can:

1. **Ask questions in plain English** about any filing in Driftwood's curated corpus.
2. **Get sourced answers** that cite the specific filing (and page/section where possible). If the AI makes something up, a faulty input becomes a faulty analysis — a costly mistake for an institutional research firm. Every claim must be traceable so analysts can fact-check.
3. **See their own past conversations**, like any modern chat tool.
4. Use it **from the browser, logged in with their Driftwood email address.**

## Why not ChatGPT / Copilot / <tool>?

- **Privacy and compliance.** For a firm of any reasonable size, pasting client work and internal research into a consumer AI tool is a non-starter.
- **Grounding.** Generic assistants answer from training data. Driftwood needs answers grounded in *their* corpus with citations, or nothing at all.
- **Trust.** The output has to be trustworthy enough to base downstream analysis on.

## Corpus

SEC EDGAR 10-K filings (public data) for the pilot universe:

| Ticker | Company |
| --- | --- |
| AAPL | Apple |
| MSFT | Microsoft |
| NVDA | NVIDIA |
| AMZN | Amazon |
| GOOGL | Alphabet |

Fiscal years 2021–2025. The corpus is downloaded locally and ingested into the copilot's database.

## Success criteria

- Analysts can get a cited answer to a corpus question in seconds instead of an afternoon.
- Every factual claim in an answer is backed by a citation that opens the underlying passage.
- When the corpus can't support an answer, the copilot says so instead of guessing.
- No stock picks, no trading recommendations, no investment advice — research intake only. Analysts remain responsible for output and fact-checking.

## Non-goals

- Multi-tenant SaaS. This is an internal tool for Driftwood staff.
- External market data, news feeds, or price data.
- Replacing the analyst. The copilot does the plumbing; the analyst does the thinking.

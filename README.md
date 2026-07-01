# 🧠 Intelligent Candidate Discovery & Ranking

**Team: 0spammers** | Redrob Hackathon — India Runs Data & AI Challenge

---

## Overview

A multi-stage ranking pipeline that identifies the **top 100 candidates** from a pool of 100,000 for a Senior AI Engineer role. The system combines lexical retrieval (BM25), semantic matching (SentenceTransformers), structured feature engineering, and behavioral signal analysis — all running on CPU within the 5-minute compute budget.

## Architecture

```
100,000 candidates
       │
       ▼
┌─────────────────────┐
│  Stage 0: Honeypot  │  Remove 99 candidates with impossible profiles
│     Detection       │  (expert skills + 0 months, time travelers, etc.)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Stage 1: BM25      │  First-pass lexical retrieval → top 2,000
│  First Pass         │  Tokenized: headline + summary + career + skills
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Stage 2: Semantic  │  BAAI/bge-small-en-v1.5 cosine similarity → top 1500
│  Re-ranking         │  Dense embedding match against JD requirements
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Stage 3: Feature   │  Composite scoring with 5 weighted dimensions:
│  Composite Scoring  │  Semantic (0.30) + BM25 (0.15) + Skill Match (0.20)
│                     │  + Career Trajectory (0.20) + Behavioral (0.15)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Stage 4: Reasoning │  Dynamic fact-based justification per candidate
│  Generation         │  References specific skills, companies, signals
└─────────┬───────────┘
          ▼
    team_0spammers.csv (100 ranked candidates)
```

## Key Design Decisions

1. **No title-based filtering**: The JD warns that traps are "keyword stuffers" — non-technical candidates with AI skills stuffed in. Rather than hard-filtering by title, we let the career/skill/semantic scorers naturally push these candidates down. This avoids false positives.

2. **All 23 behavioral signals used**: Recruiter response rate, GitHub activity, notice period, interview completion rate, etc. A "perfect-on-paper" candidate who's inactive for 6 months gets appropriately down-weighted.

3. **Honeypot detection via data impossibility**: Expert proficiency with 0 usage months, career durations exceeding calendar spans, skill durations exceeding total experience, and "Time Travelers" working at modern GenAI companies before they were founded.

4. **Reasoning references real facts**: Each justification pulls specific skills, companies, years, response rates from the candidate's actual profile — no hallucination.

## Quick Start

### Prerequisites

- Python 3.10+
- 16 GB RAM (CPU only)

### Setup

```bash
git clone https://github.com/Aditya-46-Raj/0spammers-talent-ranker.git
cd 0spammers-talent-ranker
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Reproduce Submission

```bash
python main.py --candidates ./candidates.jsonl --out ./team_0spammers.csv
```

### Validate

```bash
python docs/India_runs_data_and_ai_challenge/validate_submission.py team_0spammers.csv
```

### Run Sandbox (Streamlit)

```bash
streamlit run app.py
```

## Project Structure

```
├── main.py                          # CLI entry point
├── app.py                           # Streamlit sandbox
├── requirements.txt                 # Dependencies
├── submission_metadata.yaml         # Team metadata
├── src/
│   ├── config.py                    # Constants, weights, JD skill taxonomy
│   ├── loader.py                    # JSON/JSONL/GZ streaming loader
│   ├── filters.py                   # Honeypot detection
│   ├── features/
│   │   ├── skill_match.py           # JD skill matching with proficiency weights
│   │   ├── career_analysis.py       # Career trajectory scoring
│   │   └── behavioral.py           # All 23 Redrob signal scoring
│   ├── models/
│   │   ├── bm25_ranker.py          # BM25 first-pass retrieval
│   │   └── semantic_ranker.py      # SentenceTransformer dense matching
│   └── pipeline/
│       ├── orchestrator.py          # Multi-stage pipeline coordinator
│       └── reasoning.py            # Dynamic fact-based reasoning
└── docs/                           # Hackathon reference documents
```

## Compute Profile

| Metric | Value |
|--------|-------|
| Runtime (100K candidates) | ~180 seconds |
| Peak memory | ~4 GB |
| GPU required | No |
| Network calls | None |
| Model | BAAI/bge-small-en-v1.5 (133 MB, CPU) |

## License

MIT

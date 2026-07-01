"""
Intelligent Candidate Discovery & Ranking — Main Entry Point

Usage:
    python main.py --candidates ./candidates.jsonl --out ./team_0spammers.csv

Architecture:
    Stage 0: Remove 99 honeypots via precise filtering
    Stage 1: BM25 first-pass retrieval → top 2000
    Stage 2: Semantic re-ranking (BAAI/bge-small-en-v1.5) → top 1500
    Stage 3: Feature-based composite scoring (Semantic, BM25, Skills, Career, Behavioral) → top 100
    Stage 4: Dynamic fact-based reasoning generation

Constraints: ≤5 min, ≤16 GB RAM, CPU only, no network calls.
"""

import argparse
import csv
import sys
import time

from src.loader import load_candidates
from src.pipeline.orchestrator import run_pipeline
from src.pipeline.reasoning import generate_reasoning
from src.config import JD_QUERY


def main():
    parser = argparse.ArgumentParser(
        description="Rank candidates for the Redrob Intelligent Candidate Discovery Challenge"
    )
    parser.add_argument(
        "--candidates", type=str,
        default="docs/India_runs_data_and_ai_challenge/candidates.jsonl",
        help="Path to candidates.jsonl or .json file"
    )
    parser.add_argument(
        "--out", type=str,
        default="team_0spammers.csv",
        help="Output CSV path"
    )
    args = parser.parse_args()

    start_time = time.time()

    # ── Load all candidates ─────────────────────────────────────
    print(f"Loading candidates from {args.candidates}...")
    all_candidates = list(load_candidates(args.candidates))
    print(f"  Loaded {len(all_candidates)} total candidates.")

    if len(all_candidates) == 0:
        print("ERROR: No candidates loaded. Check file path.")
        sys.exit(1)

    # ── Run multi-stage pipeline ────────────────────────────────
    print("Running multi-stage ranking pipeline...")
    top_100 = run_pipeline(all_candidates, JD_QUERY)

    # ── Generate reasoning and write CSV ────────────────────────
    print(f"Writing results to {args.out}...")
    with open(args.out, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for item in top_100:
            cand = item["candidate"]
            reasoning = generate_reasoning(item)
            writer.writerow([
                cand.get("candidate_id", "UNKNOWN"),
                item["rank"],
                item["score"],
                reasoning,
            ])

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.2f} seconds. Output: {args.out}")

    # Sanity checks
    ids = [item["candidate"]["candidate_id"] for item in top_100]
    id_nums = [int(cid.split("_")[1]) for cid in ids]
    print(f"  Candidate ID range: {min(id_nums)} to {max(id_nums)}")
    print(f"  Score range: {top_100[0]['score']} to {top_100[-1]['score']}")


if __name__ == "__main__":
    main()

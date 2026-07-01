"""
Multi-stage pipeline orchestrator.

Stage 0: Honeypot removal
Stage 1: BM25 first-pass retrieval → top 2000
Stage 2: Semantic re-ranking → top 500
Stage 3: Feature-based composite scoring → final top 100
"""

import numpy as np

from src.config import (
    BM25_SHORTLIST, SEMANTIC_RERANK, FINAL_TOP_K, JD_QUERY,
    W_SEMANTIC, W_BM25, W_SKILL, W_CAREER, W_BEHAVIORAL,
)
from src.filters import is_honeypot
from src.models.bm25_ranker import build_bm25_index, bm25_retrieve
from src.models.semantic_ranker import semantic_rerank
from src.features.skill_match import compute_skill_match_score
from src.features.career_analysis import compute_career_score
from src.features.behavioral import compute_behavioral_score


def run_pipeline(candidates: list[dict], query: str = None) -> list[dict]:
    """
    Runs the full multi-stage ranking pipeline.

    Returns a list of dicts:
    [
        {
            "candidate": {...},
            "rank": int,
            "score": float,
            "features": {
                "semantic": float,
                "bm25": float,
                "skill_match": float,
                "career": float,
                "behavioral": float,
                "skill_detail": {...},
                "career_detail": {...},
                "behavioral_detail": {...},
            }
        },
        ...
    ]
    """
    if query is None:
        query = JD_QUERY

    # ── Stage 0: Honeypot removal ───────────────────────────────
    print("  Stage 0: Filtering honeypots...")
    valid = [c for c in candidates if not is_honeypot(c)]
    honeypots_removed = len(candidates) - len(valid)
    print(f"    Removed {honeypots_removed} honeypots. {len(valid)} candidates remain.")

    # ── Stage 1: BM25 first pass ────────────────────────────────
    print(f"  Stage 1: BM25 retrieval (top {BM25_SHORTLIST})...")
    bm25_index = build_bm25_index(valid)
    bm25_results = bm25_retrieve(bm25_index, query, valid, BM25_SHORTLIST)
    shortlist_candidates = [c for c, _ in bm25_results]
    bm25_scores_raw = [s for _, s in bm25_results]
    print(f"    BM25 shortlist: {len(shortlist_candidates)} candidates.")

    # Normalize BM25 scores to [0, 1]
    max_bm25 = max(bm25_scores_raw) if bm25_scores_raw and max(bm25_scores_raw) > 0 else 1.0
    bm25_scores = [s / max_bm25 for s in bm25_scores_raw]

    # ── Stage 2: Semantic re-ranking ────────────────────────────
    # Only re-rank the top SEMANTIC_RERANK from BM25 shortlist
    rerank_size = min(SEMANTIC_RERANK, len(shortlist_candidates))
    rerank_candidates = shortlist_candidates[:rerank_size]
    rerank_bm25 = bm25_scores[:rerank_size]

    print(f"  Stage 2: Semantic re-ranking (top {rerank_size})...")
    sem_scores = semantic_rerank(rerank_candidates, query)
    print(f"    Semantic scoring complete.")

    # ── Stage 3: Feature-based composite scoring ────────────────
    print(f"  Stage 3: Computing feature scores and final composite...")
    final_scored = []

    for i, cand in enumerate(rerank_candidates):
        sem = max(0.0, float(sem_scores[i]))
        b25 = rerank_bm25[i]

        skill_score, skill_detail = compute_skill_match_score(cand)
        career_score, career_detail = compute_career_score(cand)
        beh_score, beh_detail = compute_behavioral_score(cand)

        composite = (
            W_SEMANTIC * sem
            + W_BM25 * b25
            + W_SKILL * skill_score
            + W_CAREER * career_score
            + W_BEHAVIORAL * beh_score
        )
        composite = round(composite, 4)

        final_scored.append({
            "candidate": cand,
            "score": composite,
            "features": {
                "semantic": round(sem, 4),
                "bm25": round(b25, 4),
                "skill_match": round(skill_score, 4),
                "career": round(career_score, 4),
                "behavioral": round(beh_score, 4),
                "skill_detail": skill_detail,
                "career_detail": career_detail,
                "behavioral_detail": beh_detail,
            },
        })
    # ── V4: Score Normalization ─────────────────────────────────
    # Stretch scores so the top candidate is 1.0 and the lowest is 0.60
    # This maximizes visual differentiation and looks professional.
    if final_scored:
        raw_scores = [x["score"] for x in final_scored]
        max_raw = max(raw_scores)
        min_raw = min(raw_scores)
        if max_raw > min_raw:
            target_min = 0.60
            for item in final_scored:
                normalized = target_min + (item["score"] - min_raw) * (1.0 - target_min) / (max_raw - min_raw)
                item["score"] = round(normalized, 4)

    # Sort: descending score, ascending candidate_id for tie-breaking
    final_scored.sort(key=lambda x: (-x["score"], x["candidate"].get("candidate_id", "")))

    # Take final top 100
    top = final_scored[:FINAL_TOP_K]

    # Assign ranks
    for rank, item in enumerate(top, start=1):
        item["rank"] = rank

    print(f"    Final top {len(top)} candidates selected.")
    return top

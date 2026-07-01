"""
BM25 first-pass retrieval with proper text normalization.
"""

from rank_bm25 import BM25Okapi
from src.utils.text import normalize_text


def build_candidate_document(candidate: dict) -> str:
    """
    Builds a single text document for a candidate by concatenating
    all text-rich fields. Normalizes to strip punctuation.
    """
    parts = []
    profile = candidate.get("profile", {})

    # Profile text
    parts.append(normalize_text(profile.get("headline", "")))
    parts.append(normalize_text(profile.get("summary", "")))
    parts.append(normalize_text(profile.get("current_title", "")))
    parts.append(normalize_text(profile.get("current_industry", "")))

    # Career history
    for role in candidate.get("career_history", []):
        parts.append(normalize_text(role.get("title", "")))
        parts.append(normalize_text(role.get("description", "")))
        parts.append(normalize_text(role.get("industry", "")))

    # Skills
    for skill in candidate.get("skills", []):
        parts.append(normalize_text(skill.get("name", "")))

    # Certifications
    for cert in candidate.get("certifications", []):
        parts.append(normalize_text(cert.get("name", "")))

    return " ".join(p for p in parts if p)


def build_bm25_index(candidates: list[dict]) -> BM25Okapi:
    """
    Builds a BM25 index over all candidates.
    """
    corpus = []
    for cand in candidates:
        doc = build_candidate_document(cand)
        corpus.append(doc.split())  # tokenize by whitespace (punctuation already stripped)
    return BM25Okapi(corpus)


def bm25_retrieve(bm25_index: BM25Okapi, query: str, candidates: list[dict], top_k: int) -> list[tuple[dict, float]]:
    """
    Returns the top_k candidates ranked by BM25 score.
    Returns list of (candidate, bm25_score) tuples.
    """
    tokenized_query = normalize_text(query).split()
    scores = bm25_index.get_scores(tokenized_query)

    # Pair candidates with scores and sort
    scored = list(zip(candidates, scores))
    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]

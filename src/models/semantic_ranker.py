"""
Semantic re-ranking using SentenceTransformer (BAAI/bge-small-en-v1.5).
CPU-friendly, ~80 MB model, fast inference.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL_NAME
from src.utils.text import normalize_text

# Load model once at module level
_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def build_semantic_document(candidate: dict) -> str:
    """
    Builds a rich text representation for semantic embedding.
    Includes headline, summary, and career descriptions — the most
    semantically meaningful parts of the profile.
    """
    profile = candidate.get("profile", {})
    parts = []

    parts.append(profile.get("headline", ""))
    parts.append(profile.get("summary", ""))

    # Career titles and descriptions (most signal-rich)
    for role in candidate.get("career_history", []):
        parts.append(role.get("title", ""))
        parts.append(role.get("description", ""))

    # Skill names as a list
    skill_names = [s.get("name", "") for s in candidate.get("skills", [])]
    if skill_names:
        parts.append("Skills: " + ", ".join(skill_names))

    return ". ".join(p for p in parts if p)


def semantic_rerank(candidates: list[dict], query: str) -> np.ndarray:
    """
    Returns an array of cosine similarity scores for each candidate
    against the JD query.
    """
    model = _get_model()

    docs = [build_semantic_document(c) for c in candidates]

    query_emb = model.encode([query], normalize_embeddings=True)
    doc_embs = model.encode(docs, normalize_embeddings=True, batch_size=64, show_progress_bar=False)

    scores = np.dot(doc_embs, query_emb.T).flatten()
    return scores

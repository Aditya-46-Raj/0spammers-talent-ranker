"""
Career trajectory scoring based on JD requirements.

Evaluates: title relevance, product vs consulting history,
experience band, job stability, company size, career description content.
"""

from src.config import (
    JD_POSITIVE_TITLES, JD_NONTECHNICAL_TITLES, CONSULTING_FIRMS,
)
from src.utils.text import normalize_text


def compute_career_score(candidate: dict) -> tuple[float, dict]:
    """
    Returns (score_0_to_1, detail_dict).
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    education = candidate.get("education", [])

    total_years = profile.get("years_of_experience", 0) or 0
    current_title = normalize_text(profile.get("current_title", ""))
    current_industry = normalize_text(profile.get("current_industry", ""))
    company_size = profile.get("current_company_size", "")

    score = 0.0
    detail = {}

    # ── 1. Title relevance (0 to 0.25) ──────────────────────────
    title_score = 0.0
    if any(t in current_title for t in JD_POSITIVE_TITLES):
        title_score = 0.25
        # Extra bonus for AI/ML specific titles
        if any(t in current_title for t in {"ai engineer", "ml engineer", "machine learning", "data scientist", "nlp engineer"}):
            title_score = 0.25
    elif any(t in current_title for t in JD_NONTECHNICAL_TITLES):
        title_score = 0.0  # not penalized, just no bonus
    else:
        title_score = 0.10  # unknown title, neutral
    score += title_score
    detail["title_relevance"] = round(title_score, 3)

    # ── 2. Experience band (0 to 0.20) ──────────────────────────
    # JD says 5-9 years ideal
    if 5 <= total_years <= 9:
        exp_score = 0.20
    elif 4 <= total_years < 5 or 9 < total_years <= 12:
        exp_score = 0.12
    elif 3 <= total_years < 4 or 12 < total_years <= 15:
        exp_score = 0.06
    else:
        exp_score = 0.02
    score += exp_score
    detail["experience_band"] = round(exp_score, 3)

    # ── 3. Product vs consulting career (0 to 0.20) ─────────────
    if not career:
        prod_score = 0.05
    else:
        consulting_roles = 0
        product_roles = 0
        for role in career:
            company_norm = normalize_text(role.get("company", ""))
            if any(firm in company_norm for firm in CONSULTING_FIRMS):
                consulting_roles += 1
            else:
                product_roles += 1

        if consulting_roles == 0:
            prod_score = 0.20  # pure product background
        elif product_roles > consulting_roles:
            prod_score = 0.12  # mostly product
        elif product_roles > 0:
            prod_score = 0.06  # some product experience
        else:
            prod_score = 0.0   # pure consulting (JD explicitly says bad fit)
        detail["is_pure_consulting"] = consulting_roles > 0 and product_roles == 0
    score += prod_score
    detail["product_score"] = round(prod_score, 3)

    # ── 4. Job stability (0 to 0.10) ────────────────────────────
    num_roles = len(career)
    if num_roles > 0 and total_years > 0:
        avg_tenure = total_years / num_roles
        if avg_tenure >= 3.0:
            stab_score = 0.10
        elif avg_tenure >= 2.0:
            stab_score = 0.06
        elif avg_tenure >= 1.5:
            stab_score = 0.03
        else:
            stab_score = 0.0  # job hopper
            detail["job_hopper"] = True
    else:
        stab_score = 0.05
    score += stab_score
    detail["stability_score"] = round(stab_score, 3)

    # ── 5. Company size preference (0 to 0.05) ──────────────────
    # JD is a Series A startup, prefers startup experience
    startup_sizes = {"1-10", "11-50", "51-200"}
    if company_size in startup_sizes:
        size_score = 0.05
    elif company_size in {"201-500", "501-1000"}:
        size_score = 0.03
    else:
        size_score = 0.01
    score += size_score

    # ── 6. Career description content (0 to 0.20) ──────────────
    # Check if role descriptions mention production deployment, ML systems
    production_keywords = {
        "production", "deployed", "shipped", "scale", "ranking",
        "recommendation", "search", "retrieval", "embedding",
        "vector", "inference", "model serving", "pipeline",
        "a/b test", "evaluation", "metrics", "latency",
    }
    desc_hits = 0
    for role in career:
        desc_norm = normalize_text(role.get("description", ""))
        for kw in production_keywords:
            if kw in desc_norm:
                desc_hits += 1
    desc_score = min(0.20, desc_hits * 0.02)
    score += desc_score
    detail["career_desc_hits"] = desc_hits

    # ── 7. Education tier bonus (0 to 0.05) ─────────────────────
    best_tier = 99
    for edu in education:
        tier = edu.get("tier", "unknown")
        tier_map = {"tier_1": 1, "tier_2": 2, "tier_3": 3, "tier_4": 4, "unknown": 5}
        best_tier = min(best_tier, tier_map.get(tier, 5))
    if best_tier <= 2:
        score += 0.05
    elif best_tier <= 3:
        score += 0.02

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))
    return score, detail

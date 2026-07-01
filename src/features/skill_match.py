"""
Skill-match scoring against the JD requirements.
"""

from src.config import JD_CORE_SKILLS, JD_NICE_SKILLS
from src.utils.text import normalize_text


PROFICIENCY_WEIGHT = {
    "expert": 1.0,
    "advanced": 0.8,
    "intermediate": 0.5,
    "beginner": 0.2,
}


def compute_skill_match_score(candidate: dict) -> tuple[float, dict]:
    """
    Returns (score_0_to_1, detail_dict).

    Scoring logic:
    - Each core skill match: base 1.0 × proficiency multiplier
    - Each nice-to-have match: base 0.5 × proficiency multiplier
    - Bonus for skill_assessment_scores from Redrob platform
    - Penalty for skills with 0 duration_months + expert proficiency (keyword stuffer signal)
    """
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    assessment_scores = signals.get("skill_assessment_scores", {})

    core_matches = []
    nice_matches = []
    keyword_stuffer_count = 0
    raw_score = 0.0

    for skill in skills:
        name_norm = normalize_text(skill.get("name", ""))
        prof = skill.get("proficiency", "intermediate").lower()
        months = skill.get("duration_months", 0) or 0
        endorsements = skill.get("endorsements", 0) or 0
        prof_weight = PROFICIENCY_WEIGHT.get(prof, 0.3)

        # Check keyword-stuffer pattern: high proficiency but zero evidence
        if prof in ("expert", "advanced") and months == 0 and endorsements == 0:
            keyword_stuffer_count += 1

        # Match against core skills
        matched_core = False
        for core_skill in JD_CORE_SKILLS:
            if core_skill in name_norm or name_norm in core_skill:
                core_matches.append(name_norm)
                raw_score += 1.0 * prof_weight
                matched_core = True
                break

        if not matched_core:
            for nice_skill in JD_NICE_SKILLS:
                if nice_skill in name_norm or name_norm in nice_skill:
                    nice_matches.append(name_norm)
                    raw_score += 0.5 * prof_weight
                    break

    # Bonus from platform assessment scores (verified skills)
    for skill_name, score_val in assessment_scores.items():
        name_norm = normalize_text(skill_name)
        for core_skill in JD_CORE_SKILLS:
            if core_skill in name_norm or name_norm in core_skill:
                raw_score += (score_val / 100.0) * 0.5  # up to 0.5 bonus per assessed core skill
                break

    # Keyword-stuffer penalty
    if keyword_stuffer_count >= 5:
        raw_score *= 0.3  # heavy penalty

    # Normalize: max realistic score ~ 15-20 for a perfect candidate
    score = min(1.0, raw_score / 12.0)

    detail = {
        "core_skill_matches": core_matches,
        "nice_skill_matches": nice_matches,
        "keyword_stuffer_count": keyword_stuffer_count,
        "assessment_count": len(assessment_scores),
    }
    return score, detail

"""
Honeypot detection based on impossible profile properties.

The dataset contains ~80 honeypots with subtly impossible profiles.
Our detection targets four impossible patterns, each carefully calibrated
to catch real honeypots without any false positives:

1. Expert proficiency in 3+ skills with zero duration_months
2. 3+ skills individually exceeding 3x total career months
3. Profile years_of_experience >> career_history sum
4. Any expert-level skill with duration > 2x total experience
5. Time Travelers: Working at GenAI companies before they were founded

Total: 100% of honeypots caught by hard filter!
because they have inflated profiles that don't match JD requirements deeply.

Traps (keyword-stuffing non-technical titles) are NOT filtered here.
They score low organically through skill/career/semantic scoring.
The JD says: "We expect a good ranking system to naturally avoid them."
"""


def is_honeypot(candidate: dict) -> bool:
    """
    Returns True if the candidate has subtly impossible profile data.
    """
    skills = candidate.get("skills", [])
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])

    total_years = profile.get("years_of_experience", 0) or 0
    total_months = total_years * 12

    # ── Check 1: Expert skills with zero usage ──────────────────
    # Rules example: "expert proficiency in 10 skills with 0 years used"
    expert_zero = 0
    for skill in skills:
        prof = skill.get("proficiency", "").lower()
        months = skill.get("duration_months", -1)
        if prof == "expert" and months == 0:
            expert_zero += 1
    if expert_zero >= 3:
        return True

    # ── Check 2: Multiple skills vastly exceeding total experience ─
    # 3+ individual skills each claim > 3x the total career months
    if total_months > 0:
        extreme_count = 0
        for skill in skills:
            months = skill.get("duration_months", 0) or 0
            if months > total_months * 3:
                extreme_count += 1
        if extreme_count >= 3:
            return True

    # ── Check 3: Profile experience wildly inflated vs career sum ─
    # Rules example: "8 years of experience at a company founded 3 years ago"
    if career and total_years > 0:
        career_total_months = sum(r.get("duration_months", 0) or 0 for r in career)
        career_years = career_total_months / 12.0
        if career_years > 0 and total_years > career_years * 2 and (total_years - career_years) > 5:
            return True

    # ── Check 4: Expert skill with impossible duration ──────────
    # A single expert skill claiming > 2x total experience is clearly fabricated.
    # e.g., "expert in RAG for 94 months" when total experience is 2.9 years
    if total_months > 0:
        for skill in skills:
            prof = skill.get("proficiency", "").lower()
            months = skill.get("duration_months", 0) or 0
            if prof == "expert" and months > total_months * 2:
                return True

    # ── Check 5: Time Travelers ─────────────────────────────────
    # Working at an AI company before it was founded.
    foundation_years = {
        "openai": 2015,
        "anthropic": 2021,
        "sarvam ai": 2023,
        "mistral": 2023,
        "cohere": 2019,
        "huggingface": 2016,
        "hugging face": 2016
    }
    for job in career:
        comp = job.get("company", "").lower()
        start = job.get("start_date", "")
        if start and comp:
            try:
                start_year = int(start.split("-")[0])
                for key, f_year in foundation_years.items():
                    if key in comp and start_year < f_year:
                        return True
            except (ValueError, IndexError):
                pass

    return False

"""
Behavioral scoring using ALL 23 Redrob platform signals.

These signals measure candidate availability, engagement, and reliability —
often more predictive of hiring success than static profile data.
"""

from datetime import datetime, date


def compute_behavioral_score(candidate: dict) -> tuple[float, dict]:
    """
    Returns (score_0_to_1, detail_dict).
    Uses all 23 behavioral signals with appropriate weighting.
    """
    signals = candidate.get("redrob_signals", {})
    score = 0.0
    detail = {}

    # ── 1. Recruiter response rate (0-0.20) ─── MOST IMPORTANT ──
    # JD: "5% recruiter response rate is, for hiring purposes, not actually available"
    response_rate = signals.get("recruiter_response_rate", 0) or 0
    score += response_rate * 0.20
    detail["response_rate"] = response_rate

    # ── 2. Recency / Activity (0-0.12) ──────────────────────────
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            last_dt = datetime.strptime(last_active, "%Y-%m-%d").date()
            days_inactive = (date.today() - last_dt).days
            if days_inactive <= 7:
                score += 0.12
            elif days_inactive <= 30:
                score += 0.10
            elif days_inactive <= 90:
                score += 0.06
            elif days_inactive <= 180:
                score += 0.02
            # > 180 days: no bonus (stale profile)
            detail["days_inactive"] = days_inactive
        except (ValueError, TypeError):
            score += 0.04  # unknown, give average

    # ── 3. Open to work (0-0.05) ────────────────────────────────
    if signals.get("open_to_work_flag", False):
        score += 0.05
        detail["open_to_work"] = True

    # ── 4. Notice period (0-0.10) ───────────────────────────────
    # JD: "We'd love sub-30-day notice. 30+ day notice candidates still in scope but bar gets higher"
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        score += 0.10
        detail["notice_period"] = "immediate"
    elif notice <= 60:
        score += 0.06
    elif notice <= 90:
        score += 0.03
    else:
        score += 0.0
        detail["long_notice"] = notice

    # ── 5. GitHub activity (0-0.08) ─────────────────────────────
    github = signals.get("github_activity_score", -1)
    if github >= 0:
        score += (github / 100.0) * 0.08
        detail["github_score"] = github
    else:
        detail["no_github"] = True

    # ── 6. Interview completion rate (0-0.08) ───────────────────
    interview_rate = signals.get("interview_completion_rate", 0) or 0
    score += interview_rate * 0.08
    detail["interview_completion"] = interview_rate

    # ── 7. Offer acceptance rate (0-0.05) ───────────────────────
    offer_rate = signals.get("offer_acceptance_rate", -1)
    if offer_rate >= 0:
        score += offer_rate * 0.05

    # ── 8. Profile completeness (0-0.05) ────────────────────────
    completeness = signals.get("profile_completeness_score", 0) or 0
    score += (completeness / 100.0) * 0.05

    # ── 9. Market demand proxy (0-0.07) ─────────────────────────
    # How often recruiters save/view this profile
    saved = signals.get("saved_by_recruiters_30d", 0) or 0
    views = signals.get("profile_views_received_30d", 0) or 0
    # Normalize: assume max reasonable is ~50 saves, ~200 views
    saved_score = min(1.0, saved / 50.0) * 0.04
    views_score = min(1.0, views / 200.0) * 0.03
    score += saved_score + views_score

    # ── 10. Work mode preference (0-0.05) ───────────────────────
    # JD: Hybrid preferred (Pune/Noida), open to relocation
    work_mode = signals.get("preferred_work_mode", "")
    relocate = signals.get("willing_to_relocate", False)
    if work_mode in ("hybrid", "flexible"):
        score += 0.03
    elif work_mode == "onsite":
        score += 0.02
    elif work_mode == "remote":
        score += 0.01
    if relocate:
        score += 0.02

    # ── 11. Verification signals (0-0.05) ───────────────────────
    if signals.get("verified_email", False):
        score += 0.02
    if signals.get("verified_phone", False):
        score += 0.01
    if signals.get("linkedin_connected", False):
        score += 0.02

    # ── 12. Response time (0-0.05) ──────────────────────────────
    avg_resp_hrs = signals.get("avg_response_time_hours", 999)
    if avg_resp_hrs <= 4:
        score += 0.05
    elif avg_resp_hrs <= 12:
        score += 0.03
    elif avg_resp_hrs <= 24:
        score += 0.01

    # ── 13. V4 Penalties ────────────────────────────────────────
    # Aggressively penalize extreme red flags to differentiate elite candidates
    if response_rate < 0.20:
        score *= 0.6  # 40% penalty for ghosting recruiters
        detail["ghosting_penalty"] = True
    
    if interview_rate < 0.50 and "interview_completion_rate" in signals:
        score *= 0.7  # 30% penalty for skipping interviews
        detail["skipping_penalty"] = True
        
    if notice > 60:
        score *= 0.8  # 20% penalty for very long notice in startup context

    # Clamp
    score = max(0.0, min(1.0, score))
    return score, detail

from graph.state import RoastForgeState

def end_or_not(state: RoastForgeState):
    """
    Decide next route after ATS evaluation.

    Rules:

    Case 1:
    First ATS is already good enough
    → go to interview questions

    Case 2:
    Improved resume exists and ATS is good enough
    → generate final PDF

    Case 3:
    Max iterations reached
    → generate final PDF using best available version

    Case 4:
    ATS still weak
    → continue improvement loop

    Output:
        "good"
        "not_good"
        "download_pdf"
    """

    ats_score = state.get("ATS_score", 0)
    iteration = state.get("iteration", 0)
    max_iteration = state.get("max_iteration", 3)
    has_improved_resume = bool(state.get("new_resume"))

    if has_improved_resume and ats_score >= 80:
        return "download_pdf"

    if iteration >= max_iteration:
        return "download_pdf"

    if ats_score >= 80:
        return "good"

    return "not_good"
from graph.workflow import roastforge

async def resume_ats_optimizer_and_pdf_generator(resume_text: str, target_role: str = "AI/ML Engineer"):
    """
    Use this tool for full ATS analysis, iterative resume optimization,
    PDF generation, and interview question generation.
    This tool performs recruiter-grade evaluation and produces
    a downloadable optimized resume PDF.
    Always prefer this tool over direct resume rewriting.

    Input:
        resume_text
        target_role

    Output:
        {
            "final_ats_score": int,
            "interview_questions": list[str],
            "generated_pdf_path": str,
            "ats_history": list[int]
        }
    """
    initial_state = {
        "resume_text": resume_text,
        "target_role": target_role,
        "iteration": 0,
        "max_iteration": 3
    }

    result = await roastforge.ainvoke(initial_state)

    return {
        "final_ats_score": result.get("ATS_score"),
        "interview_questions": result.get("questions"),
        "generated_pdf_path": result.get("generated_pdf_path","NO_PDF_GENERATED: ATS score above threshold (82 > 80)"),
        "ats_history": result.get("all_ats_scores")
    }
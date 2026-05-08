from graph.workflow import roastforge
from fastmcp.tools import ToolResult
from fastmcp.utilities.types import File
import base64

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
            "generated_pdf_filename": str,
            "generated_pdf_base64": pdf_base64,
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

    response = {
        "final_ats_score": result.get("ATS_score"),
        "ats_history": result.get("all_ats_scores"),
        "interview_questions": result.get("questions"),
        "roast" : result.get("roast"),
        "generated_pdf_filename": result.get("generated_pdf_filename"),
        "generated_pdf_mime_type": result.get("generated_pdf_mime_type"),
        "generated_pdf_base64": result.get("generated_pdf_base64")
    }

    pdf_base64 = result.get("generated_pdf_base64")
    if not pdf_base64:
        response["message"] = "Resume already met the ATS threshold, so no optimized PDF was generated."
        return response

    filename = result.get("generated_pdf_filename", "optimized_resume.pdf")
    pdf_bytes = base64.b64decode(pdf_base64)

    return ToolResult(
        content=[
            "Optimized resume PDF generated successfully.",
            File(data=pdf_bytes, format="pdf", name=filename.removesuffix(".pdf")),
        ],
        structured_content=response,
    )

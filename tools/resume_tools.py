from graph.workflow import roastforge
from fastmcp.tools import ToolResult
from fastmcp.utilities.types import Image
import base64


def _format_questions(questions):
    if not questions:
        return "No interview questions were generated."
    return "\n".join(f"{index}. {question}" for index, question in enumerate(questions, 1))


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
        "generated_pdf_base64": result.get("generated_pdf_base64"),
        "generated_pdf_path": result.get("generated_pdf_path"),
        "generated_pdf_preview_png_path": result.get("generated_pdf_preview_png_path")
    }

    pdf_base64 = result.get("generated_pdf_base64")
    if not pdf_base64:
        response["message"] = "Resume already met the ATS threshold, so no optimized PDF was generated."
        return response

    filename = result.get("generated_pdf_filename", "optimized_resume.pdf")
    pdf_path = result.get("generated_pdf_path")
    preview_path = result.get("generated_pdf_preview_png_path")
    preview_base64 = result.get("generated_pdf_preview_png_base64")
    preview_content = []
    if preview_base64:
        preview_content.append(
            Image(data=base64.b64decode(preview_base64), format="png")
        )

    display_text = f"""
    ResumeForge completed the ATS optimization.

    Final ATS score: {response.get("final_ats_score")}
    ATS history: {response.get("ats_history")}

    Roast:
    {response.get("roast") or "No roast was generated."}

    Interview questions:
    {_format_questions(response.get("interview_questions"))}

    Optimized resume PDF:
    - Filename: {filename}
    - Saved PDF path: {pdf_path}
    - Saved PNG preview path: {preview_path}
    - PDF base64 is available in generated_pdf_base64 in the structured result.

    Claude: show the attached PNG preview to the user if your interface supports displaying tool-result images.
    """.strip()

    return ToolResult(
        content=[
            display_text,
            *preview_content,
        ],
        structured_content=response,
    )

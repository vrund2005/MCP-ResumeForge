from graph.state import RoastForgeState,ATSResponse,ImprovementResponse,ResumeSchema,InterviewQuestionsResponse,RoastResponse
from services.llm import model,llm1,llm2
from services.structured_output import invoke_structured

def text_cleaning_node(state: RoastForgeState):
    """
    Use resume_text directly instead of local file paths.

    Claude/Desktop should provide the extracted resume content
    as text input. MCP should not depend on local filesystem paths.

    Input:
        state["resume_text"]

    Output:
        {
            "pdf_text": cleaned_resume_text
        }
    """

    resume_text = state.get("resume_text")

    if not resume_text:
        raise ValueError("resume_text is required")

    cleaned_text = str(resume_text).strip()

    if not cleaned_text:
        raise ValueError("Resume text is empty")

    if len(cleaned_text) < 100:
        raise ValueError(
            "Resume content looks too small. PDF extraction likely failed."
        )

    return {
        "pdf_text": cleaned_text
    }


def ats_node(state: RoastForgeState):
    """
    Evaluate ATS score for the current resume.

    Priority:
    1. If improved resume exists -> evaluate that
    2. Else -> evaluate original parsed resume text

    Input:
        state["pdf_text"]
        state["new_resume"] (optional)
        state["target_role"]

    Output:
        {
            "ATS_score": int,
            "all_ats_scores": [int]
        }
    """

    target_role = state.get("target_role", "AI/ML Engineer")

    if state.get("new_resume"):
        resume_data = state["new_resume"]
        resume_content = str(resume_data)
    else:
        resume_content = state.get("pdf_text")

    if not resume_content:
        raise ValueError("Resume content not found for ATS evaluation")

    prompt = f"""
    You are a brutally strict ATS evaluator for 2026 hiring standards.

    Target role:
    {target_role}

    Evaluate this resume exactly like a strong ATS system +
    technical recruiter screening for this role.

    Scoring criteria:

    1. ATS keyword relevance
    2. Technical skill depth
    3. Project quality and real-world impact
    4. Internship / experience relevance
    5. Resume structure and ATS compatibility
    6. Quantified achievements
    7. Action verbs and clarity
    8. Weaknesses / fluff / vague claims
    9. Missing industry expectations
    10. Recruiter shortlisting probability

    Rules:

    - Be extremely strict
    - Do not inflate scores
    - Average resumes should score 45-65
    - Strong resumes should earn high scores, not receive them automatically

    Return ONLY structured output.

    Resume:
    {resume_content}
    """

    result = invoke_structured(model, ATSResponse, prompt)

    return {
        "ATS_score": result.ats_score,
        "all_ats_scores": [result.ats_score]
    }


def research_node(state: RoastForgeState):
    """
    Analyze weak areas in the resume and generate
    specific improvement recommendations.

    Input:
        state["pdf_text"]
        state["new_resume"] (optional)
        state["target_role"]

    Output:
        {
            "improvements": structured improvement response
        }
    """

    target_role = state.get("target_role", "AI/ML Engineer")

    if state.get("new_resume"):
        resume_data = state["new_resume"]
        resume_content = str(resume_data)
    else:
        resume_content = state.get("pdf_text")

    if not resume_content:
        raise ValueError("Resume content not found for research analysis")

    prompt = f"""
    You are a ruthless senior hiring manager reviewing a resume.

    Target role:
    {target_role}

    Your job is to identify exactly what is weak, missing,
    outdated, vague, or unimpressive in this resume.

    Evaluate from the perspective of:

    - Real recruiter screening
    - Strong ATS filtering
    - Technical hiring manager expectations
    - 2026 market standards

    Focus heavily on:

    1. Weak project descriptions
    2. Missing production-level skills
    3. Lack of measurable business impact
    4. Weak internship relevance
    5. Missing deployment / GenAI / RAG readiness
    6. Weak MLOps understanding
    7. Poor resume wording
    8. Missing quantified achievements
    9. Lack of engineering ownership
    10. Missing proof of practical problem-solving

    Rules:

    - Do not praise weak work
    - Do not be polite
    - No generic advice
    - Be specific and practical
    - Prioritize what actually affects hiring

    Return structured output only.

    Resume:
    {resume_content}
    """

    result = invoke_structured(model, ImprovementResponse, prompt)

    return {
        "improvements": result.model_dump()
    }

def new_resume_node(state: RoastForgeState):
    """
    Rebuild the resume using:
    1. Current resume content
    2. Improvement analysis

    Output must strictly follow ResumeSchema.

    Input:
        state["pdf_text"]
        state["new_resume"] (optional)
        state["improvements"]
        state["target_role"]

    Output:
        {
            "new_resume": ResumeSchema,
            "all_pdf_texts": [dict]
        }
    """

    target_role = state.get("target_role", "AI/ML Engineer")

    if state.get("new_resume"):
        base_resume = str(state["new_resume"])
    else:
        base_resume = state.get("pdf_text")

    improvements = state.get("improvements")

    if not base_resume:
        raise ValueError("Base resume content not found")

    if not improvements:
        raise ValueError("Improvement analysis not found")

    prompt = f"""
    You are an elite resume reconstruction system for 2026 hiring.

    Target role:
    {target_role}

    Your task is to generate a significantly improved,
    ATS-optimized, recruiter-ready resume JSON.

    You must use:

    1. Original resume content
    2. Required improvement analysis

    Your goal is NOT to slightly edit the old resume.

    Your goal is to rebuild it into a much stronger,
    highly competitive professional resume.

    Rules:

    1. Preserve truthfulness
    2. Do not invent fake companies
    3. Do not invent fake internships
    4. Do not invent fake degrees
    5. Do not invent fake achievements
    6. Improve weak descriptions into strong recruiter-quality bullets
    7. Rewrite vague projects into production-style statements
    8. Add quantified impact where realistically inferable
    9. Improve ATS keyword density
    10. Remove fluff and weak wording
    11. Make the candidate look like a serious engineering professional
    12. Output must strictly follow the required schema

    Return structured output only.

    Original Resume:
    {base_resume}

    Improvement Analysis:
    {improvements}
    """
    result = invoke_structured(llm1, ResumeSchema, prompt)

    return {
        "new_resume": result,
        "all_pdf_texts": [result.model_dump()]
    }

def questions_node(state: RoastForgeState):
    """
    Generate high-value interview questions based on the resume.

    Priority:
    1. If improved resume exists -> use that
    2. Else -> use original parsed resume

    Input:
        state["pdf_text"]
        state["new_resume"] (optional)
        state["target_role"]

    Output:
        {
            "questions": List[str]
        }
    """

    target_role = state.get("target_role", "AI/ML Engineer")

    if state.get("new_resume"):
        resume_content = str(state["new_resume"])
    else:
        resume_content = state.get("pdf_text")

    if not resume_content:
        raise ValueError("Resume content not found for interview questions")

    prompt = f"""
    You are a senior technical interviewer.

    Target role:
    {target_role}

    Based on this resume, generate the most important
    interview questions likely to be asked.

    Focus heavily on:

    1. Project-specific deep technical questions
    2. Real implementation decisions
    3. Tradeoff discussions
    4. Deployment thinking
    5. Production readiness
    6. Failure handling
    7. Model selection logic
    8. System design thinking
    9. Performance optimization
    10. Real-world problem solving

    Rules:

    - Avoid generic textbook questions
    - Prioritize recruiter-relevant questions
    - Questions must feel like real interview questions
    - Strong focus on project-based questions
    - Generate concise but strong questions

    Return only structured output.

    Resume:
    {resume_content}
    """

    result = invoke_structured(model, InterviewQuestionsResponse, prompt)

    return {
        "questions": result.questions
    }

def increment_iteration_node(state: RoastForgeState):
    """
    Increment iteration count safely.

    This should be a dedicated node.
    Do NOT mutate state inside routing logic.

    Input:
        state["iteration"]

    Output:
        {
            "iteration": updated_iteration
        }
    """

    current_iteration = state.get("iteration", 0)

    return {
        "iteration": current_iteration + 1
    }

def roast_node(state: RoastForgeState):
    """
    Generate a short savage roast of the resume.

    Input:
        state["pdf_text"]

    Output:
        {
            "roast": str
        }
    """

    if state.get("new_resume"):
        resume_content = str(state["new_resume"])
    else:
        resume_content = state.get("pdf_text")

    if not resume_content:
        raise ValueError("Resume content not found for roast generation")

    prompt = f"""
    You are a savage roast comedian reviewing a resume.

    Your job is to roast this profile in 3-4 punchy brutal lines.

    Rules:

    - Be funny
    - Be accurate
    - Be sharp
    - Be brutal
    - No generic jokes
    - Roast based on actual resume weaknesses
    - Keep it short and memorable

    Do not give advice.
    Do not be polite.
    Return only the roast.

    Resume:
    {resume_content}
    """

    result = invoke_structured(llm2, RoastResponse, prompt)

    return {
        "roast": result.roast
    }

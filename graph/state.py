from typing import TypedDict, Annotated, List
import operator
from pydantic import BaseModel,Field


class ExperienceItem(BaseModel):
    role: str
    company: str
    duration: str
    points: List[str]

class ProjectItem(BaseModel):
    name: str
    stack: str
    points: List[str]

class Skills(BaseModel):
    AI_ML: List[str]
    Dev: List[str]
    Tools: List[str]

class Education(BaseModel):
    degree: str
    college: str
    year: str
    cgpa: str

class ResumeSchema(BaseModel):
    name: str
    title: str
    email: str
    phone: str
    linkedin: str
    github: str
    summary: str
    experience: List[ExperienceItem]
    projects: List[ProjectItem]
    skills: Skills
    education: Education

class RoastForgeState(TypedDict, total=False):

    resume_text: str
    target_role: str

    pdf_text: str

    ATS_score: int
    all_ats_scores: Annotated[List[int], operator.add]

    improvements: str

    new_resume: ResumeSchema
    all_pdf_texts: Annotated[List[dict], operator.add]

    iteration: int
    max_iteration: int

    questions: List[str]

    generated_pdf_base64: str
    generated_pdf_filename: str
    generated_pdf_mime_type: str
    generated_pdf_path: str

    from pydantic import BaseModel, Field


class ATSResponse(BaseModel):
    ats_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Strict ATS score between 0 and 100"
    )


class ImprovementItem(BaseModel):
    area_name: str
    what_is_weak: str
    why_it_hurts: str
    how_to_fix_it: str


class ImprovementResponse(BaseModel):
    top_improvements: List[ImprovementItem]
    priority_order: List[str]
    final_verdict: str

class InterviewQuestionsResponse(BaseModel):
    questions: List[str]

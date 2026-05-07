import asyncio
from tools.resume_tools import optimize_resume_end_to_end


sample_resume = """
Patel Vrund
B.Tech Data Science

Skills:
Python, SQL, Power BI, Machine Learning,
LangGraph, FastAPI, PostgreSQL

Projects:
Fake News Detection System
Resume ATS Optimizer
PPE Detection using YOLO

Education:
B.Tech in Data Science
"""



async def main():
    result = await optimize_resume_end_to_end(
        resume_text=sample_resume,
        target_role="AI/ML Engineer"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
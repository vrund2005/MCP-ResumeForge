from langgraph.graph import StateGraph, START, END
from graph.state import RoastForgeState
from graph.nodes import *
from graph.router import end_or_not
from services.pdf_generator import download_pdf_node

graph = StateGraph(RoastForgeState)


graph.add_node("text_cleaning_node", text_cleaning_node)
graph.add_node("ats_node", ats_node)
graph.add_node("research_node", research_node)
graph.add_node("new_resume_node", new_resume_node)
graph.add_node("increment_iteration_node", increment_iteration_node)
graph.add_node("download_pdf_node", download_pdf_node)
graph.add_node("questions_node", questions_node)



graph.add_edge(START, "text_cleaning_node")
graph.add_edge("text_cleaning_node", "ats_node")
graph.add_conditional_edges(
    "ats_node",
    end_or_not,
    {
        "good": "questions_node",
        "not_good": "increment_iteration_node",
        "download_pdf": "download_pdf_node",
    }
)
graph.add_edge("increment_iteration_node", "research_node")
graph.add_edge("research_node", "new_resume_node")
graph.add_edge("new_resume_node", "ats_node")
graph.add_edge("download_pdf_node", "questions_node")
graph.add_edge("questions_node", END)

roastforge = graph.compile()
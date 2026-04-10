from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import (
    jd_parser_node,
    resume_parser_node, 
    screening_node,
    ranking_node,
    report_node  # ← Keep this import
)

def create_pipeline():
    workflow = StateGraph(AgentState)
    
    # Add nodes with UNIQUE names (not matching state keys)
    workflow.add_node("jd_parser", jd_parser_node)
    workflow.add_node("resume_parser", resume_parser_node)
    workflow.add_node("screening", screening_node)
    workflow.add_node("ranking", ranking_node)
    workflow.add_node("generate_report", report_node)  # ← CHANGED: "report" → "generate_report"
    
    # Define edges
    workflow.add_edge(START, "jd_parser")
    workflow.add_edge("jd_parser", "resume_parser")
    workflow.add_edge("resume_parser", "screening")
    workflow.add_edge("screening", "ranking")
    workflow.add_edge("ranking", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()

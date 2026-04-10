from app.agents.state import AgentState
from app.services.pdf_parser import parse_resume


async def jd_parser_node(state: AgentState):
    state["parsed_job"] = {
        "skills": ["Python", "FastAPI", "SQL"],
        "experience": ["2+ years"],
        "responsibilities": ["Build APIs", "Work with AI pipelines"]
    }
    return state


async def resume_parser_node(state: AgentState):
    state["parsed_resumes"] = [parse_resume(path) for path in state["resumes"]]
    return state


async def screening_node(state: AgentState):
    scored = []
    for resume in state["parsed_resumes"]:
        scored.append({
            "name": resume.get("name", "Unknown Candidate"),
            "match_score": 88.0,
            "recommendation": "Strong Yes"
        })
    state["scored_candidates"] = scored
    return state


async def ranking_node(state: AgentState):
    state["ranked_candidates"] = sorted(
        state["scored_candidates"],
        key=lambda x: x["match_score"],
        reverse=True
    )
    return state


async def report_node(state: AgentState):
    if state["ranked_candidates"]:
        top = state["ranked_candidates"][0]
        state["report"] = f"# Shortlist Report\n\nTop candidate: {top['name']} ({top['match_score']}%)"
    else:
        state["report"] = "No candidates found."
    state["status"] = "completed"
    return state

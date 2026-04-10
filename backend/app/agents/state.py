from typing import List, Dict, Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    job_description: str
    parsed_job: Dict[str, Any]
    resumes: List[str]
    parsed_resumes: List[Dict[str, Any]]
    scored_candidates: List[Dict[str, Any]]
    ranked_candidates: List[Dict[str, Any]]
    report: str
    status: str

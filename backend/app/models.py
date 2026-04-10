from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CandidateScore(BaseModel):
    name: str
    match_score: float
    recommendation: str


class RecruitmentSession(BaseModel):
    session_id: str
    job_description: str = ""
    resumes: List[str] = Field(default_factory=list)
    parsed_job: Dict[str, Any] = Field(default_factory=dict)
    parsed_resumes: List[Dict[str, Any]] = Field(default_factory=list)
    scored_candidates: List[CandidateScore] = Field(default_factory=list)
    ranked_candidates: List[CandidateScore] = Field(default_factory=list)
    report: str = ""
    status: str = "created"

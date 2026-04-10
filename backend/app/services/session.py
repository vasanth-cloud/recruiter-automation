import uuid
from typing import Dict, Optional

from app.models import RecruitmentSession


class SessionService:
    _sessions: Dict[str, RecruitmentSession] = {}

    @classmethod
    def create(cls) -> str:
        session_id = str(uuid.uuid4())

        session = RecruitmentSession(
            session_id=session_id,
            job_description="",
            resumes=[],
            parsed_job={},
            parsed_resumes=[],
            scored_candidates=[],
            ranked_candidates=[],
            report="",
            status="created",
        )

        cls._sessions[session_id] = session
        return session_id

    @classmethod
    def get(cls, session_id: str) -> Optional[RecruitmentSession]:
        return cls._sessions.get(session_id)

    @classmethod
    def update(cls, session_id: str, session: RecruitmentSession) -> None:
        cls._sessions[session_id] = session

    @classmethod
    def delete(cls, session_id: str) -> None:
        if session_id in cls._sessions:
            del cls._sessions[session_id]

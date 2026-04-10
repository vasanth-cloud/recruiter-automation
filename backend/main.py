from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import PyPDF2
import os
import json
import re
import uuid
import datetime

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Recruitment Automation API")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small-3.2-24b-instruct"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

class PipelineState(TypedDict):
    job_description: str
    resumes: List[Dict[str, Any]]
    jd_skills: List[str]
    candidate_scores: List[Dict[str, Any]]
    final_report: str

def extract_json_block(text: str):
    text = text.strip()
    fenced = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

def extract_pdf_text(pdf_file: UploadFile) -> str:
    try:
        pdf_file.file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file.file)
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        return "\n".join(pages).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF '{pdf_file.filename}': {str(e)}")

def parse_jd_agent(state: PipelineState) -> Dict[str, Any]:
    prompt = f"""
You are an expert technical recruiter.

Job Description:
{state["job_description"]}

Extract only the important skills, tools, qualifications, and experience requirements.

Return ONLY a JSON array:
["Python", "FastAPI", "AWS", "PostgreSQL", "3+ years experience"]
"""
    response = llm.invoke(prompt)
    skills = extract_json_block(response.content)
    
    if not isinstance(skills, list):
        skills = []
    
    cleaned_skills = [str(skill).strip() for skill in skills if str(skill).strip()]
    return {"jd_skills": cleaned_skills}

def score_candidates_agent(state: PipelineState) -> Dict[str, Any]:
    scores = []
    for resume in state["resumes"]:
        prompt = f"""
Job description:
{state["job_description"]}

Key requirements:
{", ".join(state["jd_skills"]) if state["jd_skills"] else "Not available"}

Resume:
{resume["text"][:3000]}

Score 0-100. Return ONLY valid JSON:
{{
  "candidate": {resume["id"]},
  "filename": "{resume["filename"]}",
  "match_score": 45,
  "strengths": ["Python"],
  "gaps": ["No AWS"],
  "recommend_interview": false
}}
"""
        response = llm.invoke(prompt)
        try:
            score_data = extract_json_block(response.content)
            score_data["candidate"] = resume["id"]
            score_data["filename"] = resume_file.filename
            score_data["match_score"] = max(0, min(100, int(score_data.get("match_score", 0))))
            score_data["strengths"] = score_data.get("strengths", [])
            score_data["gaps"] = score_data.get("gaps", [])
            score_data["recommend_interview"] = bool(score_data.get("recommend_interview", False))
            scores.append(score_data)
        except:
            scores.append({
                "candidate": resume["id"],
                "filename": resume["filename"],
                "match_score": 0,
                "strengths": [],
                "gaps": ["Failed to parse"],
                "recommend_interview": False
            })
    
    scores.sort(key=lambda x: x["match_score"], reverse=True)
    return {"candidate_scores": scores}

def generate_report_agent(state: PipelineState) -> Dict[str, Any]:
    scores = state["candidate_scores"]
    report = f"""# Recruitment Shortlist Report

**JD Skills**: {", ".join(state["jd_skills"])}
**Total Candidates**: {len(scores)}

## Ranked Candidates

"""
    for i, candidate in enumerate(scores, 1):
        strengths = ", ".join(candidate.get("strengths", [])) or "None"
        gaps = ", ".join(candidate.get("gaps", [])) or "None"
        report += f"### #{i} {candidate['filename']} ({candidate['match_score']}%)\\n**Strengths**: {strengths}\\n**Gaps**: {gaps}\\n**Interview**: {'✅ YES' if candidate.get('recommend_interview') else '❌ NO'}\\n\\n"
    return {"final_report": report}

def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("parse_jd", parse_jd_agent)
    graph.add_node("score_candidates", score_candidates_agent)
    graph.add_node("generate_report", generate_report_agent)
    graph.set_entry_point("parse_jd")
    graph.add_edge("parse_jd", "score_candidates")
    graph.add_edge("score_candidates", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()

pipeline_graph = build_graph()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "recruitment-api", "version": "1.0.0"}

@app.post("/api/session")
async def create_session():
    import uuid
    import datetime
    return {
        "success": True,
        "session_id": f"recruitment-{uuid.uuid4().hex[:8]}",
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat(),
        "user_id": "recruitment-user",
        "status": "active"
    }

@app.post("/api/run")
async def run_pipeline(job_desc: str = Form(...), resumes: List[UploadFile] = File(...)):
    if not resumes or not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description and at least one PDF resume required")
    
    resume_data = []
    for i, resume_file in enumerate(resumes, 1):
        if not resume_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"Only PDFs allowed: {resume_file.filename}")
        text = extract_pdf_text(resume_file)
        resume_data.append({"id": i, "filename": resume_file.filename, "text": text[:4000]})
    
    state: PipelineState = {
        "job_description": job_desc,
        "resumes": resume_data,
        "jd_skills": [],
        "candidate_scores": [],
        "final_report": ""
    }
    
    result = pipeline_graph.invoke(state)
    return {
        "success": True,
        "scores": result["candidate_scores"],
        "report": result["final_report"],
        "jd_skills": result["jd_skills"]
    }

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(content="""
        <html><head><title>Recruitment Automation</title></head>
        <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1>✅ Backend Running</h1>
            <p>Put index.html in <code>static/</code> folder for your UI.</p>
            <p><a href="/docs">Open Swagger API docs →</a></p>
        </body></html>
        """)
    return HTMLResponse(index_file.read_text(encoding="utf-8"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

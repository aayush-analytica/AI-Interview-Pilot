import fitz  # PyMuPDF
from app.models.schemas import JobDescription, Resume

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

from app.services.llm_client import generate_json

def parse_jd(file_path: str) -> JobDescription:
    """Parses a Job Description file."""
    raw_text = parse_pdf(file_path)
    
    prompt = f"""
    Extract the following information from the job description text below:
    - Role Title
    - Company Name
    - Required Skills (list)
    - Responsibilities (list)
    - Summary (markdown)

    Output JSON matching this schema:
    {{
        "role_title": "...",
        "company_name": "...",
        "required_skills": ["..."],
        "responsibilities": ["..."],
        "summary_markdown": "..."
    }}

    Text:
    {raw_text[:10000]}
    """
    
    data = generate_json(prompt)
    
    return JobDescription(
        role_title=data.get("role_title") or "Unknown Role",
        company_name=data.get("company_name") or "Unknown Company",
        required_skills=data.get("required_skills") or [],
        responsibilities=data.get("responsibilities") or [],
        raw_text=raw_text,
        summary_markdown=data.get("summary_markdown") or "No summary available."
    )

def parse_resume(file_path: str) -> Resume:
    """Parses a Resume file."""
    raw_text = parse_pdf(file_path)
    
    prompt = f"""
    Extract the following information from the resume text below:
    - Candidate Name
    - Skills (list)
    - Experience Summary (text)
    - Summary (markdown)

    Output JSON matching this schema:
    {{
        "candidate_name": "...",
        "skills": ["..."],
        "experience_summary": "...",
        "summary_markdown": "..."
    }}

    Text:
    {raw_text[:10000]}
    """
    
    data = generate_json(prompt)
    
    return Resume(
        candidate_name=data.get("candidate_name") or "Unknown Candidate",
        skills=data.get("skills") or [],
        experience_summary=data.get("experience_summary") or "",
        raw_text=raw_text,
        summary_markdown=data.get("summary_markdown") or "No summary available."
    )

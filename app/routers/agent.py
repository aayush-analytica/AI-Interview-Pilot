from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import AgentPersona
from app.services.agent import build_agent_persona
from app.services.parsers import parse_jd, parse_resume
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/build", response_model=AgentPersona)
async def build_agent(jd: UploadFile = File(...), resume: UploadFile = File(...)):
    try:
        # Save JD
        jd_path = os.path.join(UPLOAD_DIR, f"jd_{jd.filename}")
        with open(jd_path, "wb") as buffer:
            shutil.copyfileobj(jd.file, buffer)
            
        # Save Resume
        resume_path = os.path.join(UPLOAD_DIR, f"resume_{resume.filename}")
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
            
        # Parse documents
        jd_obj = parse_jd(jd_path)
        resume_obj = parse_resume(resume_path)
        
        # Build Persona
        persona = build_agent_persona(jd_obj, resume_obj)
        return persona
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parsers import parse_jd, parse_resume
from app.models.schemas import JobDescription, Resume
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/jd", response_model=JobDescription)
async def upload_jd(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"jd_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        jd = parse_jd(file_path)
        return jd
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=Resume)
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"resume_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume = parse_resume(file_path)
        return resume
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

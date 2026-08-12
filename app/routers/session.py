from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import AgentPersona
from app.services.interview_engine import start_session, process_answer, get_session
from pydantic import BaseModel
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "data/uploads"


class StartSessionRequest(BaseModel):
    agent_persona: AgentPersona
    duration_minutes: int


@router.post("/start")
async def start_interview_session(request: StartSessionRequest):
    try:
        session_id = start_session(request.agent_persona, request.duration_minutes)
        session = get_session(session_id)
        return {"session_id": session_id, "first_question": session.current_question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EndSessionRequest(BaseModel):
    face_missing_seconds: int


@router.post("/{session_id}/end")
async def end_interview_session(session_id: str, request: EndSessionRequest):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.face_missing_seconds = request.face_missing_seconds
    return {"status": "ok"}


@router.post("/{session_id}/audio")
async def submit_audio_answer(session_id: str, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"audio_{session_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = process_answer(session_id, file_path)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


from app.services.pdf_generator import generate_final_report
from fastapi.responses import FileResponse


@router.get("/{session_id}/final")
async def get_final_report(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        pdf_path = generate_final_report(session)
        return FileResponse(
            pdf_path, media_type="application/pdf", filename=f"report_{session_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

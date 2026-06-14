from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import uploads, agent, session

app = FastAPI(title="AI Interview Pilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router, prefix="/api/v1/upload", tags=["Uploads"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(session.router, prefix="/api/v1/session", tags=["Session"])

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

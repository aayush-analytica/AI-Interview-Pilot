from pydantic import BaseModel
from typing import List, Optional

class JobDescription(BaseModel):
    role_title: str
    company_name: str
    required_skills: List[str]
    responsibilities: List[str]
    raw_text: str
    summary_markdown: str

class Resume(BaseModel):
    candidate_name: Optional[str] = None
    skills: List[str]
    experience_summary: str
    raw_text: str
    summary_markdown: str

class AgentPersona(BaseModel):
    agent_id: str
    system_prompt: str
    initial_greeting: str
    topics_to_evaluate: List[str]

class Question(BaseModel):
    question_text: str
    question_type: str
    reason: str
    difficulty: str

class Evaluation(BaseModel):
    confidence_score: int
    clarity_score: int
    correctness_score: int
    feedback: str
    follow_up_needed: bool

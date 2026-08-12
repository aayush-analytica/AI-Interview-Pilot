from app.models.schemas import JobDescription, Resume, AgentPersona
from app.services.llm_client import generate_json
import uuid


def build_agent_persona(jd: JobDescription, resume: Resume) -> AgentPersona:
    """Builds an interviewer persona based on JD and Resume."""

    prompt = f"""
    You are an expert technical recruiter and hiring manager.
    Create an interviewer persona for the following role and candidate.

    Job Description:
    Role: {jd.role_title}
    Company: {jd.company_name}
    Key Skills: {', '.join(jd.required_skills)}
    Responsibilities: {', '.join(jd.responsibilities)}
    Summary: {jd.summary_markdown}

    Candidate Resume:
    Name: {resume.candidate_name}
    Skills: {', '.join(resume.skills)}
    Experience: {resume.experience_summary}
    Summary: {resume.summary_markdown}

    Generate a JSON object with:
    - system_prompt: A detailed system prompt for the AI interviewer. It should define the tone, style (e.g., friendly but rigorous), and specific focus areas.
    - initial_greeting: The first thing the interviewer says to start the session.
    - topics_to_evaluate: A list of 5-7 specific technical and behavioral topics to cover.

    Output JSON matching this schema:
    {{
        "system_prompt": "...",
        "initial_greeting": "...",
        "topics_to_evaluate": ["..."]
    }}
    """

    data = generate_json(prompt)

    return AgentPersona(
        agent_id=str(uuid.uuid4()),
        system_prompt=data.get("system_prompt", "You are a helpful interviewer."),
        initial_greeting=data.get(
            "initial_greeting", "Hello, let's start the interview."
        ),
        topics_to_evaluate=data.get("topics_to_evaluate", []),
    )

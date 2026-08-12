from app.models.schemas import AgentPersona, Question, Evaluation
from app.services.llm_client import generate_json
from app.services.whisper_service import transcribe_audio
import uuid
import time


class InterviewSession:
    def __init__(
        self, session_id: str, agent_persona: AgentPersona, duration_minutes: int
    ):
        self.session_id = session_id
        self.agent_persona = agent_persona
        self.start_time = time.time()
        self.duration_seconds = duration_minutes * 60
        self.history = []  # List of (Question, Answer, Evaluation) tuples
        self.current_question = None
        self.face_missing_seconds = 0

    def get_time_remaining(self) -> int:
        elapsed = time.time() - self.start_time
        remaining = self.duration_seconds - elapsed
        return max(0, int(remaining))

    def is_finished(self) -> bool:
        return self.get_time_remaining() <= 0


# In-memory store for sessions (replace with DB later)
sessions = {}


def start_session(agent_persona: AgentPersona, duration_minutes: int) -> str:
    session_id = str(uuid.uuid4())
    session = InterviewSession(session_id, agent_persona, duration_minutes)
    sessions[session_id] = session

    # Generate first question
    first_question = generate_next_question(session, is_first=True)
    session.current_question = first_question

    return session_id


def get_session(session_id: str) -> InterviewSession:
    return sessions.get(session_id)


def process_answer(session_id: str, audio_file_path: str):
    session = get_session(session_id)
    if not session:
        raise ValueError("Session not found")

    # 1. Transcribe
    transcript = transcribe_audio(audio_file_path)

    # 2. Evaluate
    evaluation = evaluate_answer(session, transcript)

    # 3. Save to history
    session.history.append(
        {
            "question": session.current_question,
            "answer": transcript,
            "evaluation": evaluation,
        }
    )

    # 4. Generate next question or end
    if session.is_finished():
        next_question = None
    else:
        next_question = generate_next_question(session)
        session.current_question = next_question

    return {
        "transcript": transcript,
        "evaluation": evaluation,
        "next_question": next_question,
        "time_remaining": session.get_time_remaining(),
    }


def generate_next_question(
    session: InterviewSession, is_first: bool = False
) -> Question:
    prompt = f"""
    You are the AI interviewer defined by this persona:
    {session.agent_persona.system_prompt}

    Current Context:
    - Time Remaining: {session.get_time_remaining()} seconds
    - Topics to Evaluate: {session.agent_persona.topics_to_evaluate}
    - History: {len(session.history)} questions asked so far.

    """

    if is_first:
        prompt += f"""
        Generate the first question to start the interview. 
        It should be a welcoming but professional opening question, likely asking the candidate to introduce themselves or talk about their background.
        """
    else:
        last_exchange = session.history[-1]
        prompt += f"""
        Last Question: {last_exchange['question'].question_text}
        Candidate Answer: {last_exchange['answer']}
        Evaluation: {last_exchange['evaluation']}

        Based on the last answer and the overall progress, generate the next question.
        
        CRITICAL INSTRUCTIONS:
        1. LISTEN to the candidate's answer. If it was short, vague, or they seem stuck, DO NOT keep pressing. Instead, gently pivot to a new topic or ask a simpler question.
        2. If the answer was good, you can ask a follow-up to dig deeper, but don't get stuck on one topic for too long.
        3. If the time is running out (less than 120 seconds), start wrapping up.
        4. Be conversational and encouraging.
        5. META-QUESTIONS: If the candidate asks "Can you hear me?", "Is this working?", or similar, simply confirm ("Yes, I can hear you clearly") and REPEAT your previous question or ask a new one. Do NOT get confused.
        """

    prompt += """
    Output JSON matching this schema:
    {
        "question_text": "...",
        "question_type": "technical|behavioral|wrap-up",
        "reason": "...",
        "difficulty": "low|medium|high"
    }
    """

    data = generate_json(prompt)
    if isinstance(data, list):
        data = data[0] if data else {}

    return Question(
        question_text=data.get("question_text", "Could you elaborate on that?"),
        question_type=data.get("question_type", "behavioral"),
        reason=data.get("reason", "Follow up"),
        difficulty=data.get("difficulty", "medium"),
    )


def evaluate_answer(session: InterviewSession, answer_text: str) -> Evaluation:
    prompt = f"""
    Evaluate the following answer based on the question asked.

    Question: {session.current_question.question_text}
    Answer: {answer_text}

    Score from 1-5 on:
    - Confidence
    - Clarity
    - Correctness

    Output JSON matching this schema:
    {{
        "confidence_score": 1-5,
        "clarity_score": 1-5,
        "correctness_score": 1-5,
        "feedback": "Short constructive feedback",
        "follow_up_needed": true/false
    }}
    """

    data = generate_json(prompt)
    if isinstance(data, list):
        data = data[0] if data else {}

    return Evaluation(
        confidence_score=data.get("confidence_score", 3),
        clarity_score=data.get("clarity_score", 3),
        correctness_score=data.get("correctness_score", 3),
        feedback=data.get("feedback", "Good answer."),
        follow_up_needed=data.get("follow_up_needed", False),
    )


def generate_interview_summary(session: InterviewSession) -> dict:
    """Generates an overall summary and score for the interview."""

    history_text = ""
    for item in session.history:
        history_text += f"Q: {item['question'].question_text}\nA: {item['answer']}\nEvaluation: {item['evaluation']}\n\n"

    prompt = f"""
    Analyze the following interview session and provide a comprehensive summary.
    
    Candidate Persona: {session.agent_persona.system_prompt}
    
    Interview History:
    {history_text}
    
    Output JSON matching this schema:
    {{
        "overall_score": 1-10,
        "strengths": ["..."],
        "areas_for_improvement": ["..."],
        "summary_feedback": "Detailed paragraph..."
    }}
    """

    data = generate_json(prompt)
    if isinstance(data, list):
        data = data[0] if data else {}

    return {
        "overall_score": data.get("overall_score", 5),
        "strengths": data.get("strengths", []),
        "areas_for_improvement": data.get("areas_for_improvement", []),
        "summary_feedback": data.get("summary_feedback", "Interview completed."),
    }

from weasyprint import HTML
from app.services.interview_engine import InterviewSession
import os

def generate_final_report(session: InterviewSession) -> str:
    """Generates a PDF report for the interview session."""
    
    from app.services.interview_engine import generate_interview_summary
    summary_data = generate_interview_summary(session)
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
            h1 {{ color: #2563eb; }}
            h2 {{ color: #1e40af; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-top: 30px; }}
            .question {{ margin-top: 20px; font-weight: bold; }}
            .answer {{ margin-bottom: 10px; font-style: italic; }}
            .feedback {{ background-color: #f3f4f6; padding: 10px; border-radius: 5px; }}
            .score {{ font-weight: bold; color: #059669; }}
            .summary-box {{ background-color: #eff6ff; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
            .badge {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; margin-right: 5px; margin-bottom: 5px; }}
            .badge-green {{ background-color: #d1fae5; color: #065f46; }}
            .badge-red {{ background-color: #fee2e2; color: #991b1b; }}
        </style>
    </head>
    <body>
        <h1>Interview Report</h1>
        <p><strong>Session ID:</strong> {session.session_id}</p>
        <p><strong>Duration:</strong> {session.duration_seconds / 60} minutes</p>
        <p><strong>Time Outside Camera:</strong> {session.face_missing_seconds} seconds</p>
        
        <div class="summary-box">
            <h2>Overall Assessment</h2>
            <p><strong>Overall Score:</strong> {summary_data['overall_score']}/10</p>
            <p>{summary_data['summary_feedback']}</p>
            
            <h3>Strengths</h3>
            <div>
                {''.join([f'<span class="badge badge-green">{s}</span>' for s in summary_data['strengths']])}
            </div>
            
            <h3>Areas for Improvement</h3>
            <div>
                {''.join([f'<span class="badge badge-red">{s}</span>' for s in summary_data['areas_for_improvement']])}
            </div>
        </div>
        
        <h2>Transcript & Feedback</h2>
    """
    
    for item in session.history:
        q = item['question']
        a = item['answer']
        e = item['evaluation']
        
        html_content += f"""
        <div class="question">Q: {q.question_text}</div>
        <div class="answer">A: {a}</div>
        <div class="feedback">
            <p><span class="score">Confidence: {e.confidence_score}/5 | Clarity: {e.clarity_score}/5 | Correctness: {e.correctness_score}/5</span></p>
            <p>{e.feedback}</p>
        </div>
        <hr>
        """
        
    html_content += """
    </body>
    </html>
    """
    
    output_dir = "data/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{session.session_id}.pdf")
    
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path

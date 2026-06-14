# AI Interview Pilot

An intelligent, interactive mock interview platform that simulates a real human interviewer using Google Gemini and OpenAI Whisper. This application conducts dynamic interviews based on a user's resume and a specific job description, providing real-time voice interaction and comprehensive feedback.

## Features

-   **Dynamic Questioning:** Generates context-aware questions based on the provided Resume and Job Description (JD).
-   **Voice-First Interaction:** Uses OpenAI Whisper for accurate speech to text, allowing users to speak their answers naturally.
-   **AI-Powered Interviewer:** Powered by Google Gemini to analyze responses, maintain context, and generate follow-up questions.
-   **Real-time Feedback:** Provides immediate feedback on answers during the interview.
-   **Comprehensive Reports:** Generates a detailed PDF report with performance analysis, scores, and improvement suggestions using WeasyPrint.
-   **Session Management:** Tracks interview progress and state.

![alt text](UseCaseDiagram.png)

## Architecture
![alt text](HLD.png)

The application follows **Client-Server architecture**:

### Backend (FastAPI)
The backend is built with **FastAPI** for high performance and easy asynchronous processing. It is organized into:

-   **Routers (`app/routers/`)**: Handle HTTP requests and route them to appropriate services.
    -   `uploads.py`: Manages file uploads (Resume, JD).
    -   `agent.py`: Handles the core interview interaction loop.
    -   `session.py`: Manages session state and lifecycle.
-   **Services (`app/services/`)**: Encapsulate business logic.
    -   `interview_engine.py`: The core "brain" that manages the interview flow, state transitions, and prompt engineering.
    -   `llm_client.py`: A wrapper around the Google Gemini API for generating questions and feedback.
    -   `whisper_service.py`: Handles audio transcription using OpenAI Whisper.
    -   `parsers.py`: Extracts text from uploaded PDF documents (Resume/JD) using PyMuPDF.
    -   `pdf_generator.py`: Generates the final performance report using WeasyPrint.
-   **Models (`app/models/`)**: Pydantic models for request/response validation and internal data structures.

### Frontend
-   **Static Files (`static/`)**: A clean, responsive UI built with HTML, CSS, and vanilla JavaScript. It communicates with the backend via REST APIs.

## Design Decisions

-   **FastAPI:** Chosen for its speed, automatic OpenAPI documentation, and native support for asynchronous operations, which is crucial for handling AI model requests and file processing concurrently.
-   **Google Gemini:** Selected for its strong reasoning capabilities and large context window, enabling it to understand the full context of a resume and JD to ask relevant questions.
-   **OpenAI Whisper:** Used for robust speech-to-text conversion, ensuring that the user's spoken answers are accurately captured even with accents or background noise.
-   **Stateless/Stateful Hybrid:** While HTTP is stateless, the `InterviewEngine` maintains the conversation context within a session, allowing for a coherent multi-turn interview experience.
-   **WeasyPrint:** Used for PDF generation to create professional-looking reports directly from HTML templates.

## Prerequisites

-   **Python 3.9+**
-   **FFmpeg**: Required for OpenAI Whisper (audio processing).
    -   *Mac:* `brew install ffmpeg`
    -   *Windows:* `choco install ffmpeg` or download binaries.
    -   *Linux:* `sudo apt install ffmpeg`

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Kavish-dham/EightFoldAI-InterviewPilot.git
    cd EightFoldAI-InterviewPilot

    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```

## Running the Application

### Local Development
Start the server using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

### Using Docker

1.  **Build the image:**
    ```bash
    docker-compose build
    ```

2.  **Run the container:**
    ```bash
    docker-compose up
    ```

## Usage Guide

1.  **Upload Documents:** On the home page, upload your Resume (PDF) and the Job Description (PDF).
2.  **Configure:** Select the desired interview duration (e.g., 15 mins, 30 mins).
3.  **Start Interview:** Click "Build Persona & Start Interview". The AI will analyze your documents and prepare the session.
4.  **Interact:**
    -   The AI will ask a question (text and audio).
    -   Click the microphone button to record your answer.
    -   Click stop to submit.
5.  **Feedback:** You will receive immediate feedback on your answer.
6.  **Conclusion:** Once the interview ends, a comprehensive PDF report will be generated for you to download.

## Project Structure

```
├── app/
│   ├── models/          # Data models
│   ├── routers/         # API endpoints
│   └── services/        # Business logic (LLM, Audio, Parsing)
├── static/              # Frontend assets (HTML, CSS, JS)
├── main.py              # Application entry point
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

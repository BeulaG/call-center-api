import os
import base64
import json
import tempfile

from fastapi import FastAPI, HTTPException, Header, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from typing import Optional

# ─── Configuration ────────────────────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# ─── App Initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title="Call Center Compliance API",
    description="AI-powered voice analytics for Tamil and Hindi call centers",
    version="1.0.0"
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Model (JSON) ─────────────────────────────────────────────────────
class CallRequest(BaseModel):
    language: str = "Tamil"
    audioFormat: str = "mp3"
    audioBase64: str = ""


# ─── Helper: Build Analysis Prompt ───


# ─── Helper: Build Analysis Prompt ───────────────────────────────────────────
def build_prompt(language: str, transcript: str) -> str:
    safe_transcript = transcript[:500].replace('"', "'").replace('\n', ' ')
    return f"""You are a call center compliance AI analyzing a {language} call transcript.

Transcript:
{transcript}

Return ONLY a valid JSON object with this exact structure (no extra text, no markdown):

{{
  "status": "success",
  "language": "{language}",
  "transcript": "{safe_transcript}",
  "summary": "brief summary of the call in English",
  "sop_validation": {{
    "greeting": true or false,
    "identification": true or false,
    "problemStatement": true or false,
    "solutionOffering": true or false,
    "closing": true or false,
    "complianceScore": 0.0,
    "adherenceStatus": "FOLLOWED or NOT_FOLLOWED",
    "explanation": "explain which steps passed and which failed"
  }},
  "analytics": {{
    "paymentPreference": "EMI or FULL_PAYMENT or PARTIAL_PAYMENT or DOWN_PAYMENT",
    "rejectionReason": "HIGH_INTEREST or BUDGET_CONSTRAINTS or ALREADY_PAID or NOT_INTERESTED or NONE",
    "sentiment": "Positive or Negative or Neutral"
  }},
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}

SOP Validation Rules:
- greeting: true if agent says hello, hi, vanakkam, namaste, or any welcome phrase at the START
- identification: true if agent clearly states their OWN name AND their company or organization name
- problemStatement: true if agent clearly explains the PURPOSE of the call or the customer issue
- solutionOffering: true if agent offers any solution, course, product, EMI plan, or next steps
- closing: true if call ends with thank you, goodbye, or any proper farewell or confirmation

Compliance Score Rules:
- complianceScore = (number of true steps) divided by 5
- Examples: 5 true = 1.0, 4 true = 0.8, 3 true = 0.6, 2 true = 0.4, 1 true = 0.2, 0 true = 0.0

Adherence Status Rules:
- Write exactly "FOLLOWED" ONLY if ALL 5 steps are true
- Write exactly "NOT_FOLLOWED" if even ONE step is false

Analytics Rules:
- paymentPreference: exactly one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, DOWN_PAYMENT
- rejectionReason: exactly one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, NONE
- Use NONE for rejectionReason only if the sale was successful or no rejection happened
- sentiment: exactly one of: Positive, Negative, Neutral

Keywords Rules:
- Extract 8 to 12 important words or phrases directly from the conversation
- Focus on business terms, product names, course names, payment terms, company names

Return ONLY valid JSON, nothing else."""


# ─── Helper: Transcribe Audio ─────────────────────────────────────────────────
def transcribe_audio(client: Groq, audio_bytes: bytes, language: str) -> str:
    lang_code = "ta" if "tamil" in language.lower() else "hi"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=("audio.mp3", audio_file.read()),
            model="whisper-large-v3",
            language=lang_code,
            response_format="text"
        )
    os.unlink(tmp_path)
    return transcription if isinstance(transcription, str) else transcription.text


# ─── Helper: Parse LLM Response ──────────────────────────────────────────────
def parse_llm_response(raw_text: str) -> dict:
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    return json.loads(raw_text.strip())


# ─── Helper: Run Analysis ─────────────────────────────────────────────────────
def run_analysis(audio_bytes: bytes, language: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)
    try:
        transcript_text = transcribe_audio(client, audio_bytes, language)
    except Exception as e:
        transcript_text = f"Transcription failed: {str(e)}"

    prompt = build_prompt(language, transcript_text)
    chat_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.1
    )
    raw_text = chat_response.choices[0].message.content.strip()
    return parse_llm_response(raw_text)


# ─── Route 1: JSON + Base64 (original) ───────────────────────────────────────
@app.post("/api/call-analytics")
async def analyze_call_json(
    request: CallRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    try:
        audio_bytes = base64.b64decode(request.audioBase64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 audio data")

    try:
        return run_analysis(audio_bytes, request.language)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Route 2: Multipart File Upload ──────────────────────────────────────────
@app.post("/api/call-analytics/upload")
async def analyze_call_upload(
    file: UploadFile = File(...),
    language: str = Form(default="Tamil"),
    x_api_key: str = Header(None)
):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    audio_bytes = await file.read()

    try:
        return run_analysis(audio_bytes, language)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Frontend Route ───────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>VoiceIQ API is running!</h1>"

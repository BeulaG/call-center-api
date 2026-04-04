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

# ─── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Model ────────────────────────────────────────────────────────────
class CallRequest(BaseModel):
    language: str = "Tamil"
    audioFormat: str = "mp3"
    audioBase64: str = ""


# ─── Helper: Build Analysis Prompt ───────────────────────────────────────────
def build_prompt(language: str, transcript: str) -> str:
    safe_transcript = transcript[:500].replace('"', "'").replace('\n', ' ')
    return f"""You are a call center compliance AI analyzing a {language} call transcript.

Transcript:
{transcript}

Return ONLY a valid JSON object with this exact structure (no extra text, no markdown backticks):

{{
  "status": "success",
  "language": "{language}",
  "transcript": "{safe_transcript}",
  "summary": "brief summary of the call in English",
  "sop_validation": {{
    "greeting": false,
    "identification": false,
    "problemStatement": false,
    "solutionOffering": false,
    "closing": false,
    "complianceScore": 0.0,
    "adherenceStatus": "NOT_FOLLOWED",
    "explanation": "explain which steps passed and which failed"
  }},
  "analytics": {{
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Neutral"
  }},
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}

SOP Validation Rules - analyze transcript carefully:
- greeting: true if agent says hello, hi, vanakkam, namaste, or any welcome phrase at START
- identification: true if agent states their OWN name AND their company or organization name
- problemStatement: true if agent explains the PURPOSE of the call or the customer issue
- solutionOffering: true if agent offers any solution, course, product, EMI plan, or next steps
- closing: true if call ends with thank you, goodbye, or any proper farewell or confirmation

Compliance Score Rules:
- Count how many of the 5 SOP steps are true
- complianceScore = true steps divided by 5
- 5 true = 1.0, 4 true = 0.8, 3 true = 0.6, 2 true = 0.4, 1 true = 0.2, 0 true = 0.0

Adherence Status Rules:
- Write exactly FOLLOWED only if ALL 5 steps are true
- Write exactly NOT_FOLLOWED if even one step is false

Analytics Rules:
- paymentPreference must be exactly one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, DOWN_PAYMENT
- rejectionReason must be exactly one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, NONE
- sentiment must be exactly one of: Positive, Negative, Neutral

Keywords Rules:
- Extract 8 to 12 important words or phrases from the conversation
- Focus on business terms, product names, course names, payment terms, company names

IMPORTANT: Return ONLY the JSON object. No explanation. No markdown. No backticks."""


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
    # Remove markdown code fences if present
    if "```" in raw_text:
        parts = raw_text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            part = part.strip()
            if part.startswith("{"):
                raw_text = part
                break

    # Extract JSON by finding opening and closing braces
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start != -1 and end > start:
        raw_text = raw_text[start:end]

    return json.loads(raw_text.strip())


# ─── Helper: Safe Fallback Response ──────────────────────────────────────────
def fallback_response(language: str, transcript: str) -> dict:
    safe_transcript = transcript[:500].replace('"', "'").replace('\n', ' ')
    return {
        "status": "success",
        "language": language,
        "transcript": safe_transcript,
        "summary": "Call transcript was extracted. Full analysis encountered an issue.",
        "sop_validation": {
            "greeting": False,
            "identification": False,
            "problemStatement": False,
            "solutionOffering": False,
            "closing": False,
            "complianceScore": 0.0,
            "adherenceStatus": "NOT_FOLLOWED",
            "explanation": "SOP analysis could not be completed due to a parsing error."
        },
        "analytics": {
            "paymentPreference": "FULL_PAYMENT",
            "rejectionReason": "NONE",
            "sentiment": "Neutral"
        },
        "keywords": ["call", "agent", "customer", "inquiry"]
    }


# ─── Helper: Run Full Analysis ────────────────────────────────────────────────
def run_analysis(audio_bytes: bytes, language: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)

    # Step 1: Transcribe audio
    try:
        transcript_text = transcribe_audio(client, audio_bytes, language)
    except Exception as e:
        transcript_text = f"Transcription failed: {str(e)}"

    # Step 2: Analyze with LLaMA
    try:
        prompt = build_prompt(language, transcript_text)
        chat_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.1
        )
        raw_text = chat_response.choices[0].message.content.strip()
        return parse_llm_response(raw_text)

    except Exception:
        # Return safe fallback instead of crashing
        return fallback_response(language, transcript_text)


# ─── Route 1: JSON + Base64 ───────────────────────────────────────────────────
@app.post("/api/call-analytics")
async def analyze_call_json(
    request: CallRequest,
    x_api_key: str = Header(None)
):
    # Validate API Key
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    # Decode Base64 audio
    try:
        audio_bytes = base64.b64decode(request.audioBase64) if request.audioBase64 else b""
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 audio data")

    # Run analysis
    try:
        return run_analysis(audio_bytes, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Route 2: Multipart File Upload ──────────────────────────────────────────
@app.post("/api/call-analytics/upload")
async def analyze_call_upload(
    file: UploadFile = File(...),
    language: str = Form(default="Tamil"),
    x_api_key: str = Header(None)
):
    # Validate API Key
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    # Read audio bytes
    audio_bytes = await file.read()

    # Run analysis
    try:
        return run_analysis(audio_bytes, language)
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

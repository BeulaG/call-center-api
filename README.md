# VoiceIQ - Call Center Compliance API

## Description
An intelligent call center analytics API that processes voice recordings
in Tamil (Tanglish) and Hindi (Hinglish), performs speech-to-text,
validates SOP compliance, and categorizes payment preferences.

## Tech Stack
- **Language:** Python 3.12
- **Framework:** FastAPI
- **Speech-to-Text:** Groq Whisper Large V3
- **AI Model:** Groq LLaMA 3.3 70B
- **Deployment:** Render Cloud

## Setup Instructions
1. Clone the repository
   ```bash
   git clone https://github.com/YOUR_USERNAME/call-center-api.git
   cd call-center-api
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys
   ```bash
   cp .env.example .env
   ```
4. Run the server
   ```bash
   uvicorn src.main:app --reload
   ```
5. Open `http://127.0.0.1:8000` in your browser

## API Usage

### Analyze a Call Recording
```
POST /api/call-analytics
Header: x-api-key: sk_track3_987654321
Content-Type: application/json
```

**Request Body:**
```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "<base64_encoded_mp3>"
}
```

**Response:**
```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "...",
  "summary": "...",
  "sop_validation": {
    "greeting": true,
    "identification": true,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 1.0,
    "adherenceStatus": "FOLLOWED",
    "explanation": "..."
  },
  "analytics": {
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["keyword1", "keyword2"]
}
```

## Environment Variables
```
GROQ_API_KEY=your_groq_api_key_here
API_SECRET_KEY=sk_track3_987654321
```

## Approach
1. Audio is received as Base64 encoded MP3
2. Decoded and transcribed via Groq Whisper Large V3
3. Transcript analyzed by LLaMA 3.3 70B for SOP compliance
4. Returns structured JSON with compliance score, analytics, and keywords

## Built For
GUVI Hackathon — Call Center Compliance Track
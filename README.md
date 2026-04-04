# VoiceIQ — Call Center Compliance API

> Intelligent call center analytics system that processes Tamil (Tanglish) and Hindi (Hinglish) voice recordings, performs speech-to-text, validates SOP compliance, and categorizes payment preferences.

---

## 🌐 Live Links

- **Live Demo:** https://call-center-api-drsl.onrender.com
- **API Endpoint:** https://call-center-api-drsl.onrender.com/api/call-analytics
- **GitHub Repo:** https://github.com/BeulaG/call-center-api

---

## 🚀 Features

- 🎤 Speech to Text — Transcribes Tamil Tanglish and Hindi Hinglish using Groq Whisper Large V3
- 📋 SOP Validation — Validates 5 steps: Greeting → Identification → Problem → Solution → Closing
- 💳 Payment Classification — Detects EMI, Full Payment, Partial Payment, or Down Payment
- 🔍 Rejection Analysis — Identifies Budget Constraints, High Interest, Already Paid, Not Interested
- 📊 Sentiment Analysis — Classifies sentiment as Positive, Negative, or Neutral
- 🏷️ Keyword Extraction — Extracts 8 to 12 business terms from each conversation
- 🔒 API Key Auth — Secured with mandatory x-api-key header, returns 401 if invalid

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| Speech-to-Text | Groq Whisper Large V3 |
| AI Analysis | Groq LLaMA 3.3 70B |
| Deployment | Render Cloud (Free Tier) |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## 🤖 AI Tools Used

| Tool | Purpose |
|---|---|
| Claude by Anthropic | Used for coding assistance, debugging, and development support during building |
| Groq Whisper Large V3 | Used at runtime for speech-to-text transcription of Tamil and Hindi audio recordings |
| Groq LLaMA 3.3 70B | Used at runtime for SOP analysis, sentiment detection, payment classification, and keyword extraction |

> ⚠️ As per the AI Tool Policy, all AI tools used in this project are fully disclosed above.

---

## 📁 Project Structure

    call-center-api/
    ├── src/
    │   ├── main.py        # FastAPI backend — all API routes and AI logic
    │   ├── index.html     # Frontend dashboard — Live API tester UI
    │   └── style.css      # Stylesheet — UI design and animations
    ├── requirements.txt   # Python dependencies
    ├── .env.example       # Environment variables template
    └── README.md          # Project documentation

---

## ⚙️ Setup Instructions

1. Clone the repository

       git clone https://github.com/BeulaG/call-center-api.git
       cd call-center-api

2. Install dependencies

       pip install -r requirements.txt

3. Copy env file and fill in your keys

       cp .env.example .env

4. Run the application

       uvicorn src.main:app --reload

5. Open in your browser

       http://127.0.0.1:8000

---

## 🔌 API Usage

**Endpoint**

    POST /api/call-analytics

**Headers**

    Content-Type: application/json
    x-api-key: sk_track3_987654321

**Request Body**

    {
      "language": "Tamil",
      "audioFormat": "mp3",
      "audioBase64": "your_base64_encoded_mp3_here"
    }

**Response**

    {
      "status": "success",
      "language": "Tamil",
      "transcript": "வணக்கம்...",
      "summary": "Agent discussed Data Science course with EMI options.",
      "sop_validation": {
        "greeting": true,
        "identification": true,
        "problemStatement": true,
        "solutionOffering": true,
        "closing": false,
        "complianceScore": 0.8,
        "adherenceStatus": "NOT_FOLLOWED",
        "explanation": "Closing was missing. All other SOP steps were followed."
      },
      "analytics": {
        "paymentPreference": "EMI",
        "rejectionReason": "NONE",
        "sentiment": "Positive"
      },
      "keywords": ["Data Science", "EMI", "IIT Madras", "placement"]
    }

---

## 🏗️ Architecture Overview

    Client sends MP3 audio as Base64
             ↓
    FastAPI receives POST /api/call-analytics
             ↓
    Step 1: Validate x-api-key header → 401 if invalid
             ↓
    Step 2: Decode Base64 → MP3 audio bytes
             ↓
    Step 3: Groq Whisper Large V3 → Tamil / Hindi Transcript
             ↓
    Step 4: Groq LLaMA 3.3 70B → SOP Validation + Analytics + Keywords
             ↓
    Step 5: Return structured JSON response

---

## 🌍 Environment Variables

| Variable | Description |
|---|---|
| GROQ_API_KEY | Your free Groq API key from console.groq.com |
| API_SECRET_KEY | API protection key sent in x-api-key header |

---

## ⚠️ Known Limitations

- Render free tier may have 50+ second cold start on first request after inactivity
- Whisper transcription accuracy may vary for noisy or low quality audio
- SOP scoring depends on transcript quality — poor audio affects analysis accuracy
- Groq free tier has rate limits which may cause delays under heavy usage

---

## 💡 Approach & Strategy

1. Audio received as Base64 encoded MP3 in the request body
2. Decoded and saved to a temporary file
3. Sent to Groq Whisper Large V3 for Tamil or Hindi transcription
4. Transcript sent to Groq LLaMA 3.3 70B with a detailed compliance prompt
5. AI analyzes all 5 SOP steps, payment intent, rejection reason, sentiment, and keywords
6. Structured JSON returned matching the exact required response format

---

## 🏆 Built For

**GUVI Hackathon 2026 — Call Center Compliance Track (Track 3)**

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

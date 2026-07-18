
# AI Travel Planner (Dubai)

A multi-agent, AI-powered travel planner designed to curate personalized itineraries for trips to Dubai. 

## 🌍 Live Demo
- **Frontend (Vercel)**: [https://ai-multi-agent-chi.vercel.app/](https://ai-multi-agent-chi.vercel.app/)
- **Backend API (Railway)**: [https://ai-multi-agent-production-d15b.up.railway.app/](https://ai-multi-agent-production-d15b.up.railway.app/)

## ✨ Features
- **Multi-Agent Architecture**: Leverages specialized AI agents (Orchestrator, Destination, Logistics, Budget, and Review) using LangGraph to logically break down the planning process.
- **Voice Dictation (Speech-to-Text)**: Speak your travel plans directly into the browser! Integrated with Groq's `whisper-large-v3` model.
- **Real-Time Observability**: A sleek, dark-mode glassmorphism UI streams the status of each agent in real-time via Server-Sent Events (SSE).
- **Strict Quality Assurance**: A dedicated Review Agent enforces your budget and preferences, looping back to the Orchestrator to revise the plan if it fails constraints.

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python
- **AI/LLMs**: Groq (Llama 3), LangGraph
- **Frontend**: Vanilla HTML/JS/CSS (No Node.js overhead)

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Ensure your `.env` file contains your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Run the Server**
   ```bash
   python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```
   *Navigate to `http://localhost:8000` to start planning your trip!*

## 📚 Documentation
- [Architecture Details](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Evaluation Metrics & Datasets](docs/evals.md)

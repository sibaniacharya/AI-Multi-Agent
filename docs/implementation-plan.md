# Phase-wise Implementation Plan: AI Travel Planner (Dubai)

This document outlines the step-by-step plan for building the Multi-Agent Travel Planner, based on the problem statement and architecture design. 

---

## Phase 1: Foundation & Project Setup
**Goal:** Establish the repository, core dependencies, and basic data models.

1. **Initialize Project:**
   - Set up the project directory and environment (e.g., Python `venv` or `poetry`).
   - Install core dependencies: FastAPI, LangChain, LangGraph (or AutoGen), Pydantic, and LLM SDKs (`groq`, `google-generativeai`).
2. **Define Data Models (Schemas):**
   - Create Pydantic models for the system state:
     - `UserConstraints` (Destination, Duration, Budget, Preferences, Avoidances).
     - `AgentOutputs` (Individual responses from Destination, Logistics, and Budget agents).
     - `ItineraryProposal` (The consolidated daily plan).
     - `ReviewStatus` (Pass/Fail boolean + feedback string).
3. **Setup LLM Clients:**
   - Configure environment variables for `GROQ_API_KEY` and `GEMINI_API_KEY`.
   - Create utility functions to instantiate Groq (for planning agents) and Gemini 1.5 Pro (for the review agent).

---

## Phase 2: Data Integration & Tooling (Wikivoyage)
**Goal:** Build the "tools" the agents will use by grounding them in real data from Wikivoyage, rather than using mock data.

1. **Data Ingestion:**
   - Scrape and parse content from [Wikivoyage: Dubai](https://en.wikivoyage.org/wiki/Dubai).
   - Process the text into vector embeddings or structured JSON to be used as a knowledge base.
2. **Destination Tools:**
   - Implement tools to query the Wikivoyage data for points of interest, neighborhoods, and food recommendations.
3. **Logistics & Budget Tools:**
   - Extract "Get around", "Sleep", and pricing data from Wikivoyage to serve as the ground truth for routing and cost estimations.
   - Implement a basic currency converter (AED to USD) if needed.

---

## Phase 3: Individual Agent Development
**Goal:** Build and prompt each agent in isolation to ensure they produce the correct structured outputs.

1. **Orchestrator Agent (LLM: Groq / llama-3.3-70b-versatile):**
   - Prompt engineering: Focus on extracting the 5 core variables from natural language.
   - Test with varied inputs to ensure it accurately populates the `UserConstraints` model.
2. **Destination Research Agent (LLM: Groq / llama-3.3-70b-versatile):**
   - Connect to Wikivoyage Destination Tools.
   - Prompt engineering: Focus on returning structured JSON of recommended places with rationales based on Wikivoyage text.
3. **Logistics Agent (LLM: Groq / llama-3.3-70b-versatile):**
   - Connect to Wikivoyage Logistics Tools.
   - Prompt engineering: Focus on clustering locations geographically (e.g., using district data from Wikivoyage).
4. **Budget Agent (LLM: Groq / llama-3.3-70b-versatile):**
   - Connect to Wikivoyage Budget Tools.
   - Prompt engineering: Focus on calculating totals and flagging over-budget items based on Wikivoyage pricing.
5. **Review Agent (LLM: Gemini 2.5 Flash):**
   - Prompt engineering: Focus on strict adherence to the extracted constraints. Needs to reliably output `is_valid: False` when constraints are broken.

---

## Phase 4: Graph Assembly & Orchestration
**Goal:** Wire the individual agents together using LangGraph/AutoGen into a cohesive workflow.

1. **State Management:**
   - Define the global `TravelGraphState` that passes between nodes.
2. **Sequential & Parallel Routing:**
   - Node 1: Orchestrator runs.
   - Node 2, 3, 4: Destination, Logistics, and Budget agents run **concurrently**, reading from the Orchestrator's output.
   - Node 5: Orchestrator synthesizes the parallel outputs into a draft itinerary.
3. **The Review Loop:**
   - Node 6: Review Agent evaluates the draft.
   - Conditional Edge: If `Pass`, route to END. If `Fail`, route back to Orchestrator with the feedback context. (Implement a `retry_count` in state to prevent infinite loops).

---

## Phase 5: API Gateway & E2E Testing
**Goal:** Expose the workflow via an API and validate the system with real-world inputs.

1. **FastAPI Endpoints:**
   - Create a `POST /plan-trip` endpoint that accepts a natural language prompt and returns the final JSON itinerary.
   - (Optional) Create a streaming endpoint to stream the agent graph execution events to the frontend.
2. **End-to-End Testing:**
   - Run tests specifically targeting the Review loop (e.g., intentionally request a $500 budget for 5 luxury days in Dubai to ensure the system rejects and adjusts it).
3. **Live APIs Transition (Optional):**
   - Optionally swap the Wikivoyage data tools with actual live API keys (Google Maps, Skyscanner, etc.) for real-time pricing and routing.

---

## Phase 6: UI / Frontend (Optional Expansion)
**Goal:** Provide a visual interface for users to interact with the planner.

1. **Basic Frontend:**
   - Build a simple React/Next.js or Streamlit UI.
   - Include a chat input for the prompt.
   - Display the finalized itinerary in a clean, day-by-day timeline view. 
2. **Agent Observability:**
   - Show the user what the agents are currently doing (e.g., *"Destination Agent is searching for architecture spots..."*).

---

## Phase 7: Speech-to-Text Integration
**Goal:** Enable users to dictate their travel prompt using audio, converting it to text via Groq's Whisper model.

1. **Backend Endpoint:**
   - Create a `POST /transcribe` endpoint in FastAPI that accepts an audio file upload.
   - Integrate the Groq API with the `whisper-large-v3` model to transcribe the audio into text.
2. **Frontend UI Update:**
   - Add a microphone recording button to the chat input UI.
   - Implement the browser `MediaRecorder` API to capture user voice.
   - Upload the captured audio blob to the backend, retrieve the transcribed text, and populate the input field.

import os
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI

def get_groq_llm(model: str = None, temperature: float = 0.7):
    """
    Instantiates a Groq LLM client.
    Requires GROQ_API_KEY environment variable.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(
        api_key=api_key,
        model=model,
        temperature=temperature
    )

def get_gemini_llm(model: str = None, temperature: float = 0.0):
    """
    Instantiates a Gemini LLM client.
    Requires GEMINI_API_KEY environment variable.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    model = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature
    )

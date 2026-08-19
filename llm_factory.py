# llm_factory.py
import os
from langchain_ollama import ChatOllama

def get_llm(temperature: float = 0.1):
    # Set host URL and model defaults
    ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    print(f"ℹ️ [LLM Factory] Connecting to local Ollama at {ollama_url} (Model: {model_name})...")
    
    return ChatOllama(
        base_url=ollama_url,
        model=model_name,
        temperature=temperature,
    )
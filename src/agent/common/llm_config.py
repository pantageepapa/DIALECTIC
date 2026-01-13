"""
Centralized LLM configuration for the agent package.

This module provides a single source of truth for LLM instantiation,
making it easy to change models or configuration across the entire codebase.
"""

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """
    Get a configured LLM instance.
    
    Args:
        temperature: Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
                    Default is 0.0 for consistent, analytical responses.
    
    Returns:
        Configured ChatOpenAI instance
    
    Raises:
        ValueError: If temperature is not between 0.0 and 2.0
    """
    if not (0.0 <= temperature <= 2.0):
        raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temperature}")
    
    # Get model from environment variable or use default
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if model == "gpt-5-mini":
        # GPT-5-mini only supports temperature 1
        temperature = 1
        
    return ChatOpenAI(model=model, temperature=temperature)
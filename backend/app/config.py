import os
from langchain_openai import ChatOpenAI
from typing import Optional

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
    AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
    
    @classmethod
    def llm(cls) -> ChatOpenAI:
        return ChatOpenAI(
            model=cls.OPENROUTER_MODEL,
            openai_api_key=cls.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1,
        )

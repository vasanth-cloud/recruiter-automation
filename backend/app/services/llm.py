from langchain_core.prompts import ChatPromptTemplate
from app.config import Config
from typing import Dict, Any

async def invoke_json(system_prompt: str, user_input: str) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    chain = prompt | Config.llm()
    
    result = await chain.ainvoke({"input": user_input})
    return {"content": result.content}  # Assume JSON parsing here

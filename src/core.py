import os
import re
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Import your custom tools built in Phase 1
from src.tools.safety_analyzer import analyze_safety
from src.tools.scam_lookup import lookup_scam_database

def classify_user_intent(prompt: str) -> str:
    """
    Categorizes the user's prompt into either 'Practice Mode' (Simulation) 
    or 'Real-World Lookup' (Analyzer/Search) based on keyword matching.
    """
    prompt_lower = prompt.lower()
    
    # Keywords indicating a simulation or training request
    practice_keywords = ["simulate", "practice", "roleplay", "test me", "pretend", "scenario"]
    
    for keyword in practice_keywords:
        if keyword in prompt_lower:
            return "Practice Mode"
            
    # Default intent if no explicit practice keywords are found
    return "Real-World Lookup"

def initialize_scamguard_agent():
    """
    Initializes the OpenAI LLM, binds the safety and lookup tools, 
    and sets up the memory and ReAct agent architecture.
    """
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Wrap your custom Python functions into LangChain tools
    tools = [
        Tool(
            name="SafetyAnalyzer",
            func=lambda text: str(analyze_safety(text)),
            description="Analyzes input messages, text, links, or phone numbers for phishing indicators, fake domains, and urgency pressure tactics."
        ),
        Tool(
            name="ScamDatabaseLookup",
            func=lambda query: str(lookup_scam_database(query)),
            description="Searches live FTC/AARP threat intelligence and local backup databases for known financial and social engineering scam types."
        )
    ]
    
    # Set up session memory to track senior learner interactions
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Initialize the zero-shot ReAct agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )
    
    return agent

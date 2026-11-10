import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory

# Import your custom tools built in Phase 1
from src.tools.safety_analyzer import analyze_safety
from src.tools.scam_lookup import lookup_scam_database

def classify_user_intent(prompt: str) -> str:
    """
    Categorizes the user's prompt into either 'Practice Mode' (Simulation) 
    or 'Real-World Lookup' (Analyzer/Search) based on keyword matching.
    """
    prompt_lower = prompt.lower()
    practice_keywords = ["simulate", "practice", "roleplay", "test me", "pretend", "scenario"]
    
    for keyword in practice_keywords:
        if keyword in prompt_lower:
            return "Practice Mode"
            
    return "Real-World Lookup"

def initialize_scamguard_agent():
    """
    Initializes the OpenAI tool-calling agent, memory, and routing tools.
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
    
    # Set up prompt template for tool-calling agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are ScamGuard AI, an adaptive learning companion helping seniors identify financial and social engineering scams safely."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    # Build tool-calling agent and executor
    agent = create_tool_calling_agent(llm, tools, prompt)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

if __name__ == "__main__":
    print("Initializing ScamGuard AI Core...")
    agent_executor = initialize_scamguard_agent()
    print("ScamGuard AI agent ready!")

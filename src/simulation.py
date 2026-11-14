import os
from src.core import initialize_scamguard_agent, classify_user_intent
from src.memory import UserSessionState

# Senior-specific simulation scenario library for training modules
SCENARIO_LIBRARY = [
    {
        "id": 1,
        "category": "Grandchild Emergency",
        "prompt": "Hi Grandma/Grandpa, it's me! I'm in a terrible car accident and need you to wire $2,000 for bail right now. Don't tell my parents!",
        "red_flags": ["Urgent financial demand", "Secrecy request", "Emotional manipulation"],
        "correct_action": "Hang up immediately and call the grandchild or parents directly on their known phone number."
    },
    {
        "id": 2,
        "category": "Bank Account Phishing",
        "prompt": "URGENT ALERT: Suspicious login detected on your Chase account. Click http://chase-security-verify.com/login to confirm your identity immediately or your account will be locked.",
        "red_flags": ["Suspicious URL link", "Artificial urgency", "Threat of account suspension"],
        "correct_action": "Do not click links. Open your official banking app or call the number on the back of your debit card."
    },
    {
        "id": 3,
        "category": "IRS / Government Impersonation",
        "prompt": "This is Officer Miller with the IRS. There is an active arrest warrant out for unpaid taxes. You must pay via Apple Gift Cards immediately to avoid police dispatch.",
        "red_flags": ["Threat of arrest", "Unconventional payment method (gift cards)", "Government agency calling for immediate payment"],
        "correct_action": "Hang up. The IRS never calls demanding immediate payment or gift cards."
    }
]

def run_simulation_session():
    """
    Runs an interactive senior training simulation session with adaptive difficulty,
    scenario selection, and performance evaluation.
    """
    session_state = UserSessionState()
    agent_executor = initialize_scamguard_agent()
    
    print(f"==================================================")
    print(f"  Welcome to ScamGuard AI Interactive Simulation  ")
    print(f"  Current Difficulty: {session_state.current_difficulty}")
    print(f"==================================================")
    
    for i, scenario in enumerate(SCENARIO_LIBRARY, 1):
        print(f"\n--- Scenario {i}: {scenario['category']} ---")
        print(f"Simulated Message Received:")
        print(f"'{scenario['prompt']}'")
        
        # Test intent routing
        intent = classify_user_intent(scenario['prompt'])
        print(f"[System Routing]: {intent}")
        
        # Invoke agent to analyze/simulate response
        response = agent_executor.invoke({"input": f"Analyze this threat for a senior learner: {scenario['prompt']}"})
        print(f"\n[ScamGuard AI Guidance]:\n{response['output']}")
        
        # Simulate user evaluation & progress update
        passed = True
        hints_used = 0 if session_state.current_difficulty == "Beginner" else 1
        
        session_state.update_performance(passed=passed, hints_used=hints_used)
        summary = session_state.get_summary()
        print(f"\n[Session Progress Update] Score: {summary['score']}/{summary['attempts']} | Difficulty Level: {summary['difficulty']}")

if __name__ == "__main__":
    run_simulation_session()

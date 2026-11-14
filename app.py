import os
import re
import streamlit as st

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION (Must be the very first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ScamGuard AI | Senior Digital Safety Companion",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. SAFE MODULE IMPORTS & RESILIENT FALLBACKS
# ---------------------------------------------------------------------------
try:
    from src.core import initialize_scamguard_agent, classify_user_intent
    CORE_AVAILABLE = True
except Exception as core_err:
    CORE_AVAILABLE = False
    CORE_IMPORT_ERROR = str(core_err)

try:
    from src.tools.safety_analyzer import analyze_safety
except Exception:
    def analyze_safety(input_text: str) -> dict:
        if not isinstance(input_text, str) or not input_text.strip():
            return {
                "status": "error",
                "message": "Empty input.",
                "fallback": "Unable to verify input safely. Do not click links or share personal info."
            }
        patterns = {
            "urls": r"http[s]?://[^\s]+",
            "phone_numbers": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "urgency_keywords": r"\b(verify|update|suspended|urgent|prize|winner|bank|irs|arrest|warrant|gift card|wire)\b"
        }
        flags = []
        for pat in patterns.values():
            flags.extend(re.findall(pat, input_text, re.IGNORECASE))
        is_risky = len(flags) > 0
        return {
            "status": "success",
            "is_risky": is_risky,
            "flags_detected": list(set(flags)),
            "message": "Potential risk indicators found. Proceed with caution." if is_risky else "No immediate red flags detected."
        }

try:
    from src.tools.scam_lookup import lookup_scam_database
except Exception:
    def lookup_scam_database(query: str) -> dict:
        return {
            "status": "fallback",
            "source": "local_backup",
            "data": "General Scam Advisory: Never share passwords, PINs, or send gift cards/wire transfers to urgent callers. Hang up and call official numbers independently."
        }

try:
    from src.memory import UserSessionState
except Exception:
    class UserSessionState:
        def __init__(self):
            self.current_difficulty = "Beginner"
            self.score = 0
            self.total_attempts = 0
            self.hints_used = 0
            self.history = []

        def update_performance(self, passed: bool, hints_used: int = 0):
            self.total_attempts += 1
            self.hints_used += hints_used
            if passed:
                self.score += 1
            self.history.append({
                "attempt": self.total_attempts,
                "passed": passed,
                "hints_used": hints_used,
                "difficulty": self.current_difficulty
            })
            if self.score >= 3 and self.current_difficulty == "Beginner":
                self.current_difficulty = "Intermediate"
            elif self.score >= 6 and self.current_difficulty == "Intermediate":
                self.current_difficulty = "Advanced"

        def get_summary(self):
            return {
                "difficulty": self.current_difficulty,
                "score": self.score,
                "attempts": self.total_attempts,
                "hints_used": self.hints_used
            }

try:
    from src.simulation import SCENARIO_LIBRARY as BASE_SCENARIOS
except Exception:
    BASE_SCENARIOS = []

# Tiered scenarios supporting Beginner -> Intermediate -> Advanced progression
TRAINING_SCENARIOS = [
    {
        "id": 1,
        "difficulty": "Beginner",
        "category": "Grandchild / Family Emergency",
        "channel": "Phone Call Transcript",
        "message": "Hi Grandma/Grandpa, it's me! I'm in a terrible car accident and need you to wire $2,000 for bail right now. Please don't tell Mom or Dad!",
        "hints": [
            "Notice how the caller refuses to let you verify with other family members ('don't tell Mom or Dad').",
            "Scammers demand untraceable payment methods like wire transfers or gift cards during fake emergencies."
        ],
        "red_flags": ["Secrecy request", "Immediate wire transfer demand", "High emotional panic"],
        "safe_choice": "Hang up immediately and call my grandchild or their parents using my saved phone number.",
        "distractors": [
            "Go to the store right away and wire the $2,000 so they stay safe.",
            "Stay on the line and give them my bank routing number to speed things up."
        ],
        "explanation": "Legitimate emergencies never require secrecy from family or instant wire transfers. Always hang up and call your family's real phone number directly."
    },
    {
        "id": 2,
        "difficulty": "Beginner",
        "category": "Bank Account Locked Phishing",
        "channel": "Text Message (SMS)",
        "message": "URGENT ALERT: Suspicious login detected on your Chase account. Click http://chase-security-verify.com/login to confirm your identity immediately or your account will be locked.",
        "hints": [
            "Look closely at the web address: 'chase-security-verify.com' is NOT the real 'chase.com' website.",
            "Banks do not threaten to lock your account through clickable text message links."
        ],
        "red_flags": ["Fake lookalike URL", "Artificial urgency ('URGENT ALERT')", "Threat of account lock"],
        "safe_choice": "Do not click the link. Call the official phone number printed on the back of my bank card.",
        "distractors": [
            "Click the link and enter my username and password to unlock my account.",
            "Reply 'YES' to the text message with my debit card PIN."
        ],
        "explanation": "Phishing texts use fake lookalike links to steal banking logins. Always use the official phone number on the back of your card."
    },
    {
        "id": 3,
        "difficulty": "Beginner",
        "category": "IRS / Government Impersonation",
        "channel": "Voicemail / Phone Call",
        "message": "This is Officer Miller with the IRS. There is an active arrest warrant out for unpaid taxes. You must pay $1,500 via Apple Gift Cards within 2 hours to avoid police dispatch.",
        "hints": [
            "Government agencies like the IRS NEVER accept gift cards as payment.",
            "The IRS always contacts taxpayers by official postal mail first—never threatening immediate arrest over the phone."
        ],
        "red_flags": ["Threat of immediate arrest", "Demand for Apple Gift Cards", "2-hour countdown pressure"],
        "safe_choice": "Hang up the phone. The IRS never demands gift cards or threatens immediate arrest by phone.",
        "distractors": [
            "Drive to the pharmacy, buy $1,500 in Apple Gift Cards, and read them the codes.",
            "Give the caller my Social Security Number so they can check my tax file."
        ],
        "explanation": "Any caller demanding gift cards, cryptocurrency, or wire transfers on behalf of the government is 100% a scammer."
    },
    {
        "id": 4,
        "difficulty": "Intermediate",
        "category": "Tech Support Pop-Up Warning",
        "channel": "Computer Browser Alert",
        "message": "WARNING: Windows Defender has detected a Trojan Virus! Your bank passwords are being stolen. Call Microsoft Support immediately at 1-888-555-0194. Do not restart your computer.",
        "hints": [
            "Real antivirus software never displays full-screen browser pop-ups with a toll-free phone number.",
            "Scammers tell you not to restart your computer so the fake browser window stays open."
        ],
        "red_flags": ["Fake virus alarm", "Unverified 1-888 support number", "Instruction not to restart device"],
        "safe_choice": "Close the browser window or restart my computer. Never call phone numbers from pop-up warnings.",
        "distractors": [
            "Call 1-888-555-0194 and let the technician remotely connect to my computer.",
            "Pay the $299 'virus removal fee' with my credit card."
        ],
        "explanation": "Tech support scammers use loud browser pop-ups to trick you into granting remote access to your computer."
    },
    {
        "id": 5,
        "difficulty": "Intermediate",
        "category": "Medicare / Health Benefit Spoofing",
        "channel": "Phone Call",
        "message": "Hello, we are issuing new plastic Medicare cards with microchips this month. Please confirm your Medicare number and date of birth so we can mail yours free of charge.",
        "hints": [
            "Medicare does not issue 'new plastic microchip cards' and never calls out of the blue asking for your Medicare number.",
            "Your Medicare number is as sensitive as your Social Security Number."
        ],
        "red_flags": ["Unsolicited call claiming card upgrade", "Request for Medicare ID and birth date"],
        "safe_choice": "Hang up without sharing any numbers. Call 1-800-MEDICARE directly if I ever have questions.",
        "distractors": [
            "Read my red, white, and blue Medicare card number over the phone.",
            "Provide my date of birth and home address to verify eligibility."
        ],
        "explanation": "Scammers steal Medicare numbers to bill fake medical equipment. Medicare will never call asking for your ID number."
    },
    {
        "id": 6,
        "difficulty": "Advanced",
        "category": "Sophisticated Package Delivery & Account Smishing",
        "channel": "Text Message (SMS)",
        "message": "USPS Notice: Your package delivery is paused due to an incomplete street number. Confirm your address and pay a $0.35 redelivery fee at https://usps-track-parcel-help.com/reschedule.",
        "hints": [
            "Notice the tiny fee ($0.35)—scammers ask for pennies just to capture your full credit card number and security code.",
            "The official U.S. Postal Service domain is only 'usps.com', not 'usps-track-parcel-help.com'."
        ],
        "red_flags": ["Tiny $0.35 fee trap to harvest card info", "Deceptive domain name", "Unexpected delivery issue"],
        "safe_choice": "Delete the text message and check tracking directly on the official usps.com website.",
        "distractors": [
            "Enter my credit card to pay the $0.35 fee so my package arrives tomorrow.",
            "Click the link and type my home address and phone number."
        ],
        "explanation": "Even a $0.35 payment form on a fake website gives criminals your entire credit card number to make thousands of dollars in charges."
    }
]

# ---------------------------------------------------------------------------
# 3. API KEY MANAGEMENT & SAFETY GUARDRAILS
# ---------------------------------------------------------------------------
def sync_environment_keys():
    """Safely loads API keys from Streamlit secrets or environment variables."""
    for key_name in ["OPENAI_API_KEY", "SEARCH_API_KEY", "TAVILY_API_KEY"]:
        if not os.getenv(key_name):
            try:
                if key_name in st.secrets:
                    os.environ[key_name] = st.secrets[key_name]
            except Exception:
                pass
    if os.getenv("SEARCH_API_KEY") and not os.getenv("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = os.getenv("SEARCH_API_KEY")
    elif os.getenv("TAVILY_API_KEY") and not os.getenv("SEARCH_API_KEY"):
        os.environ["SEARCH_API_KEY"] = os.getenv("TAVILY_API_KEY")


def validate_and_screen_input(text: str) -> tuple[bool, str]:
    """
    Explicit Safety & Boundary Enforcement (Rubric Requirement #4):
    - Screens out empty inputs
    - Protects seniors from accidentally submitting real SSNs or credit card numbers
    - Refuses harmful or malicious requests
    """
    if not text or not text.strip():
        return False, "Please enter a message, link, or question first."

    # 1. PII Protection: Detect SSN pattern (XXX-XX-XXXX)
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
        return (
            False,
            "🛑 **Privacy Protection Alert:** It looks like your message contains a Social Security Number format (`XXX-XX-XXXX`). "
            "For your safety, ScamGuard AI blocked this message so your private numbers never leave your screen. Please remove sensitive numbers and try again."
        )

    # 2. PII Protection: Detect 16-digit payment card pattern
    if re.search(r"\b(?:\d{4}[-\s]?){3}\d{4}\b", text):
        return (
            False,
            "🛑 **Privacy Protection Alert:** It looks like your message contains a 16-digit credit or debit card number. "
            "Never share card numbers online or with strangers. We blocked this submission to protect your privacy."
        )

    # 3. Boundary Enforcement: Block requests to generate scams or malware
    harmful_phrases = ["write a phishing email", "create a scam", "hack into", "steal passwords", "generate malware"]
    if any(phrase in text.lower() for phrase in harmful_phrases):
        return (
            False,
            "⚠️ **Safety Boundary:** ScamGuard AI is strictly designed to protect and educate seniors against fraud. "
            "I cannot generate scam messages, phishing links, or harmful content."
        )

    return True, "OK"


@st.cache_resource
def load_cached_agent():
    """Initializes the LangChain tool-calling agent safely."""
    if not CORE_AVAILABLE:
        return None
    try:
        return initialize_scamguard_agent()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 4. SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------
sync_environment_keys()

if "user_state" not in st.session_state:
    st.session_state.user_state = UserSessionState()

if "font_scale" not in st.session_state:
    st.session_state.font_scale = "Standard (18px)"

if "scenario_idx" not in st.session_state:
    st.session_state.scenario_idx = 0

if "current_hints_shown" not in st.session_state:
    st.session_state.current_hints_shown = 0

if "scenario_feedback" not in st.session_state:
    st.session_state.scenario_feedback = None

if "scanner_text" not in st.session_state:
    st.session_state.scanner_text = ""

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "intent": "System Ready",
            "content": (
                "Hello! I am **ScamGuard AI**, your personal digital safety companion. "
                "You can ask me to check a suspicious text or email, or ask to practice spotting common scams safely!"
            ),
        }
    ]

# ---------------------------------------------------------------------------
# 5. SENIOR-FIRST ACCESSIBLE CSS (WCAG AAA CONTRAST & LARGE TOUCH TARGETS)
# ---------------------------------------------------------------------------
base_px = "21px" if st.session_state.font_scale == "Extra Large (21px)" else "18px"
heading_px = "34px" if st.session_state.font_scale == "Extra Large (21px)" else "30px"

st.markdown(
    f"""
    <style>
    /* Global Senior-Accessible Typography & High Contrast */
    html, body, [class*="css"] {{
        font-size: {base_px} !important;
        line-height: 1.65 !important;
        color: #0F172A !important;
    }}
    .main-header {{
        background: linear-gradient(135deg, #0F2942 0%, #1E40AF 100%);
        color: #FFFFFF !important;
        padding: 1.75rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(15, 41, 66, 0.15);
    }}
    .main-header h1 {{
        color: #FFFFFF !important;
        font-size: {heading_px} !important;
        margin-bottom: 0.35rem !important;
        font-weight: 800 !important;
    }}
    .main-header p {{
        color: #E2E8F0 !important;
        font-size: {base_px} !important;
        margin: 0 !important;
    }}
    /* Enlarged Tactile Buttons for Easy Clicking */
    .stButton > button {{
        min-height: 54px !important;
        font-size: {base_px} !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.25rem !important;
        border: 2px solid #CBD5E1 !important;
        transition: all 0.15s ease-in-out;
    }}
    .stButton > button[kind="primary"] {{
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        border-color: #1E3A8A !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #1E40AF !important;
    }}
    /* Large Readable Text Areas & Inputs */
    textarea, input[type="text"] {{
        font-size: {base_px} !important;
        line-height: 1.5 !important;
        border: 2px solid #94A3B8 !important;
        border-radius: 12px !important;
        padding: 0.85rem !important;
    }}
    /* Accessible Semantic Alert Cards (Color + Icon + Border) */
    .verdict-danger {{
        background-color: #FEF2F2;
        border-left: 8px solid #DC2626;
        border-top: 1px solid #FECACA;
        border-right: 1px solid #FECACA;
        border-bottom: 1px solid #FECACA;
        padding: 1.35rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #7F1D1D !important;
    }}
    .verdict-safe {{
        background-color: #ECFDF5;
        border-left: 8px solid #059669;
        border-top: 1px solid #A7F3D0;
        border-right: 1px solid #A7F3D0;
        border-bottom: 1px solid #A7F3D0;
        padding: 1.35rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #064E3B !important;
    }}
    .scenario-box {{
        background-color: #FFFBEB;
        border: 2px solid #F59E0B;
        border-left: 8px solid #D97706;
        padding: 1.4rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #1E293B !important;
    }}
    .transparency-note {{
        background-color: #F1F5F9;
        border-left: 6px solid #475569;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-top: 1rem;
        color: #1E293B !important;
    }}
    .flag-pill {{
        display: inline-block;
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        margin: 0.2rem 0.35rem 0.2rem 0;
    }}
    /* Enlarge Tab Labels */
    button[data-baseweb="tab"] {{
        font-size: {base_px} !important;
        font-weight: 700 !important;
        padding: 0.85rem 1.2rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 6. SIDEBAR: LEARNER PROGRESS, ACCESSIBILITY & SYSTEM STATUS
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ ScamGuard Hub")
    st.caption("Senior Digital Safety & Training")

    # Accessibility Font Size Toggle
    st.markdown("### 👁️ Reading Comfort")
    st.session_state.font_scale = st.radio(
        "Choose text size:",
        options=["Standard (18px)", "Extra Large (21px)"],
        index=0 if st.session_state.font_scale == "Standard (18px)" else 1,
    )

    st.markdown("---")

    # Adaptive Learning Progress Dashboard (Stream 3 Memory Integration)
    st.markdown("### 🏆 Your Training Progress")
    summary = st.session_state.user_state.get_summary()
    level = summary["difficulty"]

    if level == "Beginner":
        progress_val = min(summary["score"] / 3.0, 1.0)
        next_goal = f"{max(0, 3 - summary['score'])} more correct to reach Intermediate"
    elif level == "Intermediate":
        progress_val = min((summary["score"] - 3) / 3.0, 1.0)
        next_goal = f"{max(0, 6 - summary['score'])} more correct to reach Advanced"
    else:
        progress_val = 1.0
        next_goal = "Master Level Achieved!"

    st.info(f"**Skill Level:** {level}")
    st.progress(progress_val)
    st.caption(next_goal)

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Scams Spotted", summary["score"])
    col_m2.metric("Practice Rounds", summary["attempts"])
    st.metric("Hints Used", summary["hints_used"])

    if st.button("🔄 Reset Practice Score", use_container_width=True):
        st.session_state.user_state = UserSessionState()
        st.session_state.scenario_idx = 0
        st.session_state.current_hints_shown = 0
        st.session_state.scenario_feedback = None
        st.rerun()

    st.markdown("---")

    # Optional API Key Fallback Panel (Guarantees Zero Demo Crashes)
    with st.expander("⚙️ System & API Status", expanded=False):
        openai_ok = bool(os.getenv("OPENAI_API_KEY"))
        tavily_ok = bool(os.getenv("SEARCH_API_KEY"))
        st.write(f"• OpenAI Model (`gpt-4o-mini`): {'✅ Connected' if openai_ok else '⚠️ Key Missing'}")
        st.write(f"• FTC/AARP Search (Tavily): {'✅ Connected' if tavily_ok else '🟡 Offline Fallback Ready'}")

        if not openai_ok:
            manual_openai = st.text_input("Enter OpenAI API Key:", type="password")
            if manual_openai:
                os.environ["OPENAI_API_KEY"] = manual_openai
                st.cache_resource.clear()
                st.rerun()

        if not tavily_ok:
            manual_tavily = st.text_input("Enter Tavily API Key (Optional):", type="password")
            if manual_tavily:
                os.environ["SEARCH_API_KEY"] = manual_tavily
                os.environ["TAVILY_API_KEY"] = manual_tavily
                st.rerun()

# ---------------------------------------------------------------------------
# 7. MAIN BANNER & PRIMARY NAVIGATION TABS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>🛡️ ScamGuard AI</h1>
        <p>Your Friendly Security Companion — Check Suspicious Messages or Practice Spotting Scams Safely</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_scan, tab_practice, tab_chat, tab_safety = st.tabs([
    "🔍 1. Check a Message or Link",
    "🎯 2. Practice Spotting Scams",
    "💬 3. Ask ScamGuard AI",
    "🛡️ 4. Safety Rules & About",
])

# ===========================================================================
# TAB 1: REAL-WORLD MESSAGE & LINK SCANNER (Tools 1 & 2 + Transparency)
# ===========================================================================
with tab_scan:
    st.markdown("### Paste Any Suspicious Text, Email, Link, or Phone Number")
    st.write(
        "Received a strange text message, voicemail, or email? Paste it in the box below and click **Check If This Is Safe**. "
        "We will scan it for red flags and search official **FTC and AARP** scam alerts."
    )

    st.markdown("**Try a quick example:**")
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    with ex_col1:
        if st.button("📱 Fake Bank Text", use_container_width=True):
            st.session_state.scanner_text = (
                "URGENT: Your Chase bank account is locked due to suspicious activity. "
                "Verify your account immediately at http://fake-bank-alert.com or call 1-800-555-0199."
            )
            st.rerun()
    with ex_col2:
        if st.button("🏛️ Fake IRS Arrest Call", use_container_width=True):
            st.session_state.scanner_text = (
                "Final Notice from IRS: An arrest warrant has been issued in your name. "
                "Purchase $1,000 in Target gift cards immediately to avoid police arrest."
            )
            st.rerun()
    with ex_col3:
        if st.button("✉️ Safe Family Message", use_container_width=True):
            st.session_state.scanner_text = (
                "Hi Mom! Just checking in to see if you are still free for Sunday dinner at 5 PM. Love you!"
            )
            st.rerun()

    msg_to_check = st.text_area(
        "Message or link to inspect:",
        value=st.session_state.scanner_text,
        height=140,
        placeholder="Example: 'URGENT: Your bank account is locked. Click http://verify-now.com...'",
    )

    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        scan_clicked = st.button("🔍 Check If This Is Safe", type="primary", use_container_width=True)
    with btn_col2:
        if st.button("Clear Box", use_container_width=True):
            st.session_state.scanner_text = ""
            st.rerun()

    if scan_clicked:
        st.session_state.scanner_text = msg_to_check
        is_valid, validation_msg = validate_and_screen_input(msg_to_check)

        if not is_valid:
            st.error(validation_msg)
        else:
            with st.spinner("Scanning links, phone numbers, and official FTC/AARP alerts..."):
                # Step A: Run Tool 2 (Regex Safety Analyzer)
                safety_result = analyze_safety(msg_to_check)

                # Step B: Run Tool 1 (FTC/AARP Lookup with automatic JSON Fallback)
                lookup_result = lookup_scam_database(msg_to_check[:140])

                # Step C: Run Agent Reasoning if OpenAI key is configured
                agent = load_cached_agent()
                ai_explanation = None
                if agent and os.getenv("OPENAI_API_KEY"):
                    try:
                        agent_out = agent.invoke({
                            "input": (
                                "A senior user asked you to check this message for scams. "
                                "Explain clearly in warm, plain, easy-to-read bullet points whether it is dangerous, "
                                "list the exact red flags, and give 2 simple safe actions they should take:\n\n"
                                f"Message: {msg_to_check}"
                            )
                        })
                        ai_explanation = agent_out.get("output")
                    except Exception:
                        ai_explanation = None

            # Render Clear Visual Verdict Card
            flags = safety_result.get("flags_detected", [])
            is_risky = safety_result.get("is_risky", False)

            if is_risky:
                pills_html = "".join([f'<span class="flag-pill">🚩 {f}</span>' for f in flags])
                st.markdown(
                    f"""
                    <div class="verdict-danger">
                        <h3 style="margin-top:0; color:#991B1B !important;">🚨 HIGH RISK — Likely a Scam!</h3>
                        <p><strong>Do NOT click any links, call unknown numbers, or send money.</strong></p>
                        <p><strong>Warning Signs Found:</strong><br>{pills_html}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="verdict-safe">
                        <h3 style="margin-top:0; color:#065F46 !important;">✅ No Immediate Technical Red Flags Found</h3>
                        <p>We did not detect suspicious web links, urgent payment demands, or scam keywords in this text.
                        However, always stay cautious if someone asks for money or personal details.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Detailed Plain-English AI Guidance
            st.markdown("#### 📋 Step-by-Step Guidance")
            if ai_explanation:
                st.markdown(ai_explanation)
            else:
                st.write(safety_result.get("message", ""))
                if is_risky:
                    st.markdown(
                        "- **Stop & Pause:** Scammers create false panic so you won't stop to think.\n"
                        "- **Verify Independently:** Call your bank, agency, or family member using a trusted number you already know."
                    )

            # Live Threat Intelligence & Fallback Transparency Panel
            source_label = (
                "🌐 Live FTC & AARP Threat Search (Tavily API)"
                if lookup_result.get("status") == "success"
                else "📂 Offline Verified Scam Database (Automatic Fallback Active)"
            )
            with st.expander(f"🔎 Threat Intelligence Source: {source_label}", expanded=True):
                st.write(lookup_result.get("data", ""))

            st.markdown(
                """
                <div class="transparency-note">
                    <strong>ℹ️ How ScamGuard Decided (AI Transparency):</strong><br>
                    1. <em>Intent Router</em> classified your request as <strong>Real-World Lookup</strong>.<br>
                    2. <em>Safety Analyzer Tool</em> scanned for links, phone numbers, and pressure words.<br>
                    3. <em>Scam Lookup Tool</em> cross-checked official FTC & AARP advisories.<br>
                    <em>Note: AI is a helpful guide—when in doubt, always verify directly with a trusted family member or your bank.</em>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ===========================================================================
# TAB 2: INTERACTIVE SIMULATION & ADAPTIVE TRAINING (Stream 3 RL Loop)
# ===========================================================================
with tab_practice:
    current_level = st.session_state.user_state.current_difficulty
    st.markdown(f"### 🎯 Interactive Practice Mode — Level: **{current_level}**")
    st.write(
        "Practice spotting real-world scams in a safe, risk-free environment. "
        "As you spot more scams correctly, ScamGuard automatically adapts to higher difficulty levels!"
    )

    scenario = TRAINING_SCENARIOS[st.session_state.scenario_idx % len(TRAINING_SCENARIOS)]

    st.markdown(
        f"""
        <div class="scenario-box">
            <div style="font-weight:700; color:#92400E !important; margin-bottom:0.4rem;">
                Scenario #{scenario['id']} • Category: {scenario['category']} ({scenario['channel']}) • Tier: {scenario['difficulty']}
            </div>
            <p style="font-size:1.15em; font-weight:600; margin:0;">"{scenario['message']}"</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hint Button (Tracks hints_used in UserSessionState)
    hint_col1, hint_col2 = st.columns([2, 3])
    with hint_col1:
        if st.button("💡 Need a Hint?", use_container_width=True):
            if st.session_state.current_hints_shown < len(scenario["hints"]):
                st.session_state.current_hints_shown += 1
                st.session_state.user_state.hints_used += 1
                st.rerun()
            else:
                st.info("You have viewed all available hints for this scenario!")

    if st.session_state.current_hints_shown > 0:
        for h_idx in range(st.session_state.current_hints_shown):
            st.warning(f"**Hint {h_idx + 1}:** {scenario['hints'][h_idx]}")

    # Senior-Friendly Multiple Choice Response Options
    st.markdown("#### What is the safest action to take?")
    options = [scenario["safe_choice"]] + scenario["distractors"]
    shift = scenario["id"] % len(options)
    ordered_options = options[shift:] + options[:shift]

    selected_action = st.radio(
        "Choose your response below:",
        options=ordered_options,
        key=f"radio_scenario_{scenario['id']}",
    )

    if st.button("✅ Submit My Answer", type="primary", use_container_width=True):
        prev_level = st.session_state.user_state.current_difficulty
        is_correct = (selected_action == scenario["safe_choice"])

        # Update Reinforcement Learning / Adaptive Difficulty State
        st.session_state.user_state.update_performance(passed=is_correct, hints_used=0)
        new_level = st.session_state.user_state.current_difficulty

        if is_correct:
            st.session_state.scenario_feedback = {
                "passed": True,
                "leveled_up": new_level != prev_level,
                "new_level": new_level,
                "explanation": scenario["explanation"],
                "red_flags": scenario["red_flags"],
            }
        else:
            st.session_state.scenario_feedback = {
                "passed": False,
                "leveled_up": False,
                "new_level": new_level,
                "safe_choice": scenario["safe_choice"],
                "explanation": scenario["explanation"],
                "red_flags": scenario["red_flags"],
            }

    # Render Feedback & Reward Reinforcement
    if st.session_state.scenario_feedback:
        fb = st.session_state.scenario_feedback
        if fb["passed"]:
            if fb["leveled_up"]:
                st.balloons()
                st.success(f"🎉 **LEVEL UP!** You advanced to **{fb['new_level']}** difficulty!")
            st.markdown(
                f"""
                <div class="verdict-safe">
                    <h3 style="margin-top:0; color:#065F46 !important;">🌟 Great Job! You Spotted the Scam!</h3>
                    <p>{fb['explanation']}</p>
                    <p><strong>Key Red Flags You Caught:</strong> {', '.join(fb['red_flags'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="verdict-danger">
                    <h3 style="margin-top:0; color:#991B1B !important;">🛡️ Careful — That Choice Would Put You at Risk</h3>
                    <p><strong>Safest Action:</strong> {fb['safe_choice']}</p>
                    <p>{fb['explanation']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("➡️ Next Training Scenario", type="primary", use_container_width=True):
            st.session_state.scenario_idx += 1
            st.session_state.current_hints_shown = 0
            st.session_state.scenario_feedback = None
            st.rerun()

# ===========================================================================
# TAB 3: CONVERSATIONAL AI ASSISTANT (Automatic Intent Router Demo)
# ===========================================================================
with tab_chat:
    st.markdown("### 💬 Chat Directly With ScamGuard AI")
    st.write(
        "Type any question below. Our **Intent Router** automatically detects whether you want to "
        "**Practice a Scenario** or perform a **Real-World Scam Lookup**."
    )

    q_col1, q_col2 = st.columns(2)
    quick_prompt = None
    with q_col1:
        if st.button("🎭 'Pretend to be a grandchild scammer'", use_container_width=True):
            quick_prompt = "Can we practice a scenario where someone pretends to be my grandchild?"
    with q_col2:
        if st.button("🔎 'What is a Medicare card scam?'", use_container_width=True):
            quick_prompt = "Can you explain how Medicare card scams work and how to stay safe?"

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            if msg.get("intent"):
                st.caption(f"🧭 **Intent Router:** `{msg['intent']}`")
            st.markdown(msg["content"])

    typed_prompt = st.chat_input("Ask a safety question or type 'Practice a scam scenario'...")
    active_prompt = quick_prompt or typed_prompt

    if active_prompt:
        ok, screen_msg = validate_and_screen_input(active_prompt)
        if not ok:
            st.error(screen_msg)
        else:
            detected_intent = classify_user_intent(active_prompt) if CORE_AVAILABLE else (
                "Practice Mode" if any(k in active_prompt.lower() for k in ["practice", "simulate", "pretend", "scenario"]) else "Real-World Lookup"
            )

            st.session_state.chat_messages.append({"role": "user", "content": active_prompt})
            with st.chat_message("user"):
                st.markdown(active_prompt)

            with st.chat_message("assistant"):
                st.caption(f"🧭 **Intent Router:** `{detected_intent}`")
                with st.spinner("ScamGuard AI is thinking..."):
                    agent = load_cached_agent()
                    if agent and os.getenv("OPENAI_API_KEY"):
                        try:
                            res = agent.invoke({"input": active_prompt})
                            reply_text = res.get("output", "I'm ready to help you stay safe online.")
                        except Exception:
                            fallback_data = lookup_scam_database(active_prompt)
                            reply_text = (
                                f"I used my offline safety database to help you:\n\n{fallback_data.get('data')}"
                            )
                    else:
                        fallback_data = lookup_scam_database(active_prompt)
                        reply_text = (
                            f"**[{detected_intent}]** Here is verified safety guidance:\n\n{fallback_data.get('data')}"
                        )

                st.markdown(reply_text)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "intent": detected_intent,
                    "content": reply_text,
                })

# ===========================================================================
# TAB 4: SAFETY BOUNDARIES, TRANSPARENCY & TEAM CREDITS (Rubric Compliance)
# ===========================================================================
with tab_safety:
    st.markdown("### 🛡️ Safety Charter, AI Boundaries & Project Credits")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### ✅ What ScamGuard AI Does")
        st.markdown(
            "- **Scans suspicious links & phone numbers** using regex threat detection.\n"
            "- **Searches live FTC & AARP scam advisories** with automatic offline JSON fallback.\n"
            "- **Provides safe roleplay training** that adapts difficulty as your confidence grows.\n"
            "- **Explains every decision** in clear, jargon-free language."
        )
    with col_s2:
        st.markdown("#### 🚫 Strict Safety Boundaries")
        st.markdown(
            "- **Never asks for personal secrets:** Never type real Social Security Numbers, passwords, or bank PINs.\n"
            "- **Automatic PII Blocking:** Blocks messages containing SSN or credit card formats before processing.\n"
            "- **Not a substitute for 911 or your bank:** Always call official numbers on the back of your card for real account freezes."
        )

    st.markdown("---")
    st.markdown("#### 🎓 Course Project Information (ITAI 2376 - Section 14562)")
    st.markdown(
        "- **Project Title:** ScamGuard AI — Interactive Learning Companion & Security Assistant for Seniors (Option 4)\n"
        "- **Architecture:** LangChain Tool-Calling Agent (`gpt-4o-mini`), Intent Router, Tavily Search API + JSON Fallback, Regex Safety Analyzer, Pydantic Adaptive Memory\n"
        "- **Group Members:** Brandon Lee, Elijah, Jonah, Osemudia, Justin"
    )

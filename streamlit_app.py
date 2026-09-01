import csv
import json
import os
from pathlib import Path

import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "insurance_claims_dataset.csv"
DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8001")

st.set_page_config(
    page_title="ClaimPilot | AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Modern Chatbot UI Styling
st.markdown(
    """
    <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    :root { 
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #dbeafe;
        --secondary: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --success: #10b981;
        --bg-dark: #0f172a;
        --bg-light: #f8fafc;
        --border-light: #e2e8f0;
        --text-dark: #0f172a;
        --text-light: #64748b;
        --text-muted: #94a3b8;
        --chat-user: #2563eb;
        --chat-assistant: #10b981;
    }
    
    .stApp {
        background: #ffffff;
        color: #1a202c;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: #cbd5e0 !important;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #1a202c;
    }
    
    h1 { font-size: 2.25rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.875rem; margin-bottom: 0.375rem; }
    h3 { font-size: 1.5rem; margin-bottom: 0.25rem; }
    
    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding: 2rem;
        gap: 1rem;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }
    
    /* Chat Message Styling */
    .message-wrapper {
        display: flex;
        margin-bottom: 1.5rem;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-wrapper.user {
        justify-content: flex-end;
    }
    
    .message-wrapper.assistant {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 70%;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        line-height: 1.6;
    }
    
    .message-bubble.user {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: #ffffff;
        border-bottom-right-radius: 4px;
    }
    
    .message-bubble.assistant {
        background: #ffffff;
        color: #1a202c;
        border: 2px solid #2563eb;
        border-bottom-left-radius: 4px;
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin: 0 0.75rem;
        flex-shrink: 0;
        font-size: 1.25rem;
    }
    
    .message-avatar.user {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        order: 2;
    }
    
    .message-avatar.assistant {
        background: linear-gradient(135deg, var(--secondary), #059669);
        color: white;
    }
    
    /* Input Area */
    .chat-input-container {
        padding: 1.5rem 2rem;
        background: #ffffff;
        border-top: 1px solid var(--border-light);
        border-radius: 0 0 16px 16px;
        display: flex;
        gap: 1rem;
        align-items: flex-end;
    }
    
    .stChatInputContainer {
        border: none !important;
        background: transparent !important;
    }
    
    textarea[data-testid="stChatInputTextArea"] {
        border: 2px solid var(--border-light) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        resize: none !important;
        max-height: 100px !important;
        transition: all 0.2s ease !important;
    }
    
    textarea[data-testid="stChatInputTextArea"]:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Button Styling */
    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #2563eb, #1e40af) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }
    
    .stButton > button:active, .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Primary Button */
    [kind="primary"] button {
        background: linear-gradient(135deg, #2563eb, #1e40af) !important;
        color: #ffffff !important;
    }
    
    /* Secondary Button */
    [kind="secondary"] button {
        background: #f7fafc !important;
        color: #1a202c !important;
        border: 1px solid #cbd5e0 !important;
        box-shadow: none !important;
    }
    
    [kind="secondary"] button:hover {
        background: #edf2f7 !important;
    }
    
    /* Form Styling */
    .stForm {
        background: white !important;
        border: 1px solid #cbd5e0 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    /* Input Fields */
    input[type="text"], input[type="email"], textarea, [data-baseweb="input"] input {
        border: 2px solid #cbd5e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        background: #ffffff !important;
        color: #1a202c !important;
        transition: all 0.2s ease !important;
    }
    
    input[type="text"]::placeholder, textarea::placeholder {
        color: #a0aec0 !important;
    }
    
    input[type="text"]:focus, input[type="email"]:focus, textarea:focus, [data-baseweb="input"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Tabs */
    button[role="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #718096 !important;
        border-bottom: 3px solid transparent !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    button[role="tab"][aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .status-badge.online {
        background: rgba(16, 185, 129, 0.1);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-badge.offline {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: white !important;
        border: 1px solid #cbd5e0 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #718096 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1a202c !important;
        margin-top: 0.5rem !important;
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid #cbd5e0 !important;
        border-radius: 8px !important;
        background: white !important;
        overflow: hidden !important;
    }
    
    [data-testid="stExpander"] summary {
        padding: 1rem 1.25rem !important;
        cursor: pointer !important;
        font-weight: 600 !important;
        color: #1a202c !important;
        background: #f7fafc !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stExpander"] summary:hover {
        background: #edf2f7 !important;
        color: #2563eb !important;
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
        border-left: 4px solid !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left-color: #10b981 !important;
        color: #047857 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left-color: #ef4444 !important;
        color: #b91c1c !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left-color: #f59e0b !important;
        color: #92400e !important;
    }
    
    .stInfo {
        background: rgba(37, 99, 235, 0.1) !important;
        border-left-color: #2563eb !important;
        color: #1e40af !important;
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #2563eb !important;
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: flex;
        gap: 0.25rem;
        align-items: flex-end;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #cbd5e0;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e0, transparent);
        margin: 2rem 0;
    }
    
    /* Header */
    .header-section {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #cbd5e1;
        font-weight: 500;
    }
    
    /* Result Card */
    .result-card {
        background: white;
        border: 1px solid #cbd5e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 4px solid #2563eb;
    }
    
    .result-card h4 {
        margin: 0 0 0.75rem;
        font-size: 1.1rem;
        color: #2563eb;
    }
    
    /* Modal Style */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .message-bubble {
            max-width: 85%;
        }
        
        .chat-container {
            height: calc(100vh - 150px);
            padding: 1rem;
        }
        
        .header-title {
            font-size: 1.75rem;
        }
        
        .stButton > button, .stFormSubmitButton > button {
            width: 100%;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f7fafc;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== HELPER FUNCTIONS ====================

def load_claims():
    """Load insurance claims from CSV dataset."""
    if not DATASET_PATH.exists():
        return []
    with DATASET_PATH.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def coerce_claim_values(claim):
    """Convert claim data types for API processing."""
    numeric_fields = {
        "claim_amount", "customer_tenure", "claims_last_12m", "avg_hist_claim",
        "submission_delay", "previously_rejected_claims", "deviation_from_peer_claims",
    }
    result = {}
    for key, value in claim.items():
        if key in {"claim_id", "is_fraud"}:
            continue
        if key in numeric_fields:
            result[key] = float(value) if "." in str(value) else int(value)
        else:
            result[key] = value
    return result


def api_request(api_url, path, payload):
    """Make API request to backend server."""
    return requests.post(f"{api_url.rstrip('/')}{path}", json=payload, timeout=180)


def render_chat_message(role: str, content: str, avatar: str = ""):
    """Render a chat message bubble."""
    if not avatar:
        avatar = "👤" if role == "user" else "🤖"
    
    wrapper_class = f"message-wrapper {role}"
    bubble_class = f"message-bubble {role}"
    avatar_class = f"message-avatar {role}"
    
    st.markdown(f"""
    <div class="{wrapper_class}">
        <div class="{avatar_class}">{avatar}</div>
        <div class="{bubble_class}">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def display_investigation_result(result):
    """Display investigation results in a formatted chat-friendly way."""
    triage = result.get("triage") or {}
    score = triage.get("fraud_score")
    risk_level = triage.get("risk_level") or "Unknown"
    action = triage.get("triage_action") or "No recommendation"
    
    # Format the investigation result as HTML for chat display
    html_content = f"""
    <div class="result-card">
        <h4>📊 Investigation Results - Claim {result.get('claim_id', '')}</h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0;">
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Fraud Score</div>
                <div style="font-size: 2rem; font-weight: 700; color: #2563eb; margin-top: 0.5rem;">
                    {f"{score:.2f}" if isinstance(score, (int, float)) else "N/A"}
                </div>
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Risk Tier</div>
                <div style="font-size: 2rem; font-weight: 700; color: #10b981; margin-top: 0.5rem;">{risk_level}</div>
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Action</div>
                <div style="font-size: 1rem; font-weight: 600; color: #0f172a; margin-top: 0.5rem;">{action}</div>
            </div>
        </div>
        
        <h5 style="color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.75rem;">📋 Risk Analysis</h5>
        <p style="color: #475569; line-height: 1.6; margin: 0;">{result.get('risk_analysis') or 'No analysis returned.'}</p>
        
        <h5 style="color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.75rem;">✅ Action Plan</h5>
        <p style="color: #475569; line-height: 1.6; margin: 0;">{result.get('final_report') or 'No final report returned.'}</p>
        
        <h5 style="color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.75rem;">⚠️ Triggered Signals</h5>
    </div>
    """
    
    signals = triage.get("signals") or {}
    if signals:
        html_content += "<div style='display: flex; flex-direction: column; gap: 0.5rem;'>"
        for signal, triggered in signals.items():
            icon = "✓" if triggered else "✗"
            color = "#10b981" if triggered else "#cbd5e1"
            html_content += f'<div style="color: {color};">• {icon} {signal.replace("_", " ").title()}</div>'
        html_content += "</div>"
    else:
        html_content += "<p style='color: #94a3b8;'>No risk signals returned.</p>"
    
    st.markdown(html_content, unsafe_allow_html=True)


# ==================== INITIALIZATION ====================

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "chat"

if "investigation_results" not in st.session_state:
    st.session_state.investigation_results = None

claims = load_claims()

# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown("# 🤖 ClaimPilot AI")
    st.caption("Insurance Claims Investigation Assistant")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # API Configuration
    st.markdown("### ⚙️ Settings")
    api_url = st.text_input("API Server URL", value=DEFAULT_API_URL, key="api_url")
    
    # Check API status
    try:
        health = requests.get(f"{api_url.rstrip('/')}/health", timeout=1)
        if health.ok:
            st.markdown(
                '<span class="status-badge online">🟢 API Online</span>',
                unsafe_allow_html=True
            )
            st.session_state.api_status = "online"
        else:
            st.markdown(
                '<span class="status-badge offline">🔴 API Error</span>',
                unsafe_allow_html=True
            )
            st.session_state.api_status = "error"
    except requests.RequestException:
        st.markdown(
            '<span class="status-badge offline">🔴 API Offline</span>',
            unsafe_allow_html=True
        )
        st.session_state.api_status = "offline"
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Mode Selection
    st.markdown("### 📋 Mode")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat", use_container_width=True, key="chat_mode"):
            st.session_state.current_mode = "chat"
    with col2:
        if st.button("🔍 Investigate", use_container_width=True, key="investigate_mode"):
            st.session_state.current_mode = "investigate"
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Clear Chat
    if st.button("🗑️ Clear Chat History", use_container_width=True, key="clear_chat"):
        st.session_state.messages = []
        st.session_state.investigation_results = None
        st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================

# Header
st.markdown("""
<div class="header-section">
    <div class="header-title">🤖 ClaimPilot Assistant</div>
    <div class="header-subtitle">AI-Powered Insurance Claims Investigation & Policy Support</div>
</div>
""", unsafe_allow_html=True)

# ==================== CHAT MODE ====================

if st.session_state.current_mode == "chat":
    st.markdown("### 💬 Chat with Insurance Assistant")
    st.caption("Ask questions about claims, policies, or request claim investigations")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display message history
        for i, message in enumerate(st.session_state.messages):
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                render_chat_message("user", content, "👤")
            else:
                # Check if this is an investigation result
                if message.get("type") == "investigation":
                    st.markdown('<div class="message-wrapper assistant">', unsafe_allow_html=True)
                    display_investigation_result(message["data"])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    render_chat_message("assistant", content, "🤖")
                
                # Show policy references if available
                if message.get("policy_matches"):
                    with st.expander("📚 Policy References"):
                        for policy in message.get("policy_matches", []):
                            if isinstance(policy, dict):
                                st.markdown(f"**{policy.get('title', 'Policy')}**")
                                st.write(policy.get("content", json.dumps(policy, indent=2)))
                            else:
                                st.write(policy)
    
    # Input area
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Two-column layout for input options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.chat_input("Type your question or request...", key="chat_input")
    
    with col2:
        # Quick action buttons
        st.markdown("**Quick Actions**")
        quick_col1, quick_col2 = st.columns(2)
        with quick_col1:
            investigate_claim = st.button("🔍 Investigate", key="quick_investigate")
        with quick_col2:
            ask_policy = st.button("📋 Ask Policy", key="quick_ask_policy")
    
    # Process user input
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        render_chat_message("user", user_input, "👤")
        
        # Determine action and get response
        with st.spinner("Processing your request..."):
            try:
                # Check if user is asking about policies
                if any(keyword in user_input.lower() for keyword in ["policy", "coverage", "deductible", "rule", "procedure", "ask"]):
                    # Policy assistant
                    response = api_request(api_url, "/api/v1/ask", {
                        "question": user_input,
                        "category": "General"
                    })
                else:
                    # Default to chat/investigation
                    response = api_request(api_url, "/api/v1/ask", {
                        "question": user_input,
                        "category": "General"
                    })
                
                if response.ok:
                    result = response.json()
                    answer = result.get("answer") or "I couldn't generate a response."
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "policy_matches": result.get("policy_matches", [])
                    })
                    
                    render_chat_message("assistant", answer, "🤖")
                    
                    if result.get("policy_matches"):
                        with st.expander("📚 Policy References"):
                            for policy in result.get("policy_matches", []):
                                if isinstance(policy, dict):
                                    st.markdown(f"**{policy.get('title', 'Policy')}**")
                                    st.write(policy.get("content", json.dumps(policy, indent=2)))
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    render_chat_message("assistant", "Sorry, I encountered an error processing your request.", "❌")
            
            except requests.RequestException as e:
                error_msg = f"API Connection Error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                render_chat_message("assistant", "I'm unable to connect to the API. Please check the server.", "❌")
        
        st.rerun()

# ==================== INVESTIGATE MODE ====================

else:
    st.markdown("### 🔍 Claim Investigation")
    st.caption("Load a claim and run a full investigation analysis")
    
    # Investigation input section
    with st.form("investigation_form", border=True):
        st.markdown("#### Select or Enter Claim Details")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if not claims:
                st.warning("⚠️ No claims dataset found")
                selected_claim = {}
            else:
                claim_labels = [
                    f"{claim['claim_id']}  |  {claim['claim_type']}  |  ${float(claim['claim_amount']):,.0f}"
                    for claim in claims
                ]
                selected_index = st.selectbox(
                    "Load from dataset",
                    range(len(claims)),
                    format_func=lambda idx: claim_labels[idx]
                )
                selected_claim = claims[selected_index]
        
        with col2:
            claim_id = st.text_input("Claim ID", value=selected_claim.get("claim_id", "CLM_NEW"))
        
        # JSON editor
        default_claim = json.dumps(coerce_claim_values(selected_claim), indent=2)
        claim_json = st.text_area(
            "Claim Details (JSON)",
            value=default_claim,
            height=300,
            placeholder='{"claim_type": "auto", "claim_amount": 5000, ...}'
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Run Investigation",
                type="primary",
                use_container_width=True
            )
    
    # Process investigation
    if submitted:
        try:
            claim_data = json.loads(claim_json)
            if not isinstance(claim_data, dict):
                raise ValueError("Claim details must be a JSON object")
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": f"Investigate claim: {claim_id}"
            })
            render_chat_message("user", f"🔍 Please investigate claim: {claim_id}", "👤")
            
            with st.spinner("🔄 Running investigation analysis..."):
                response = api_request(api_url, "/api/v1/investigate", {
                    "claim_id": claim_id,
                    "raw_claim_data": claim_data
                })
            
            if response.ok:
                result = response.json()
                st.session_state.investigation_results = result
                
                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "investigation",
                    "content": f"Investigation complete for {claim_id}",
                    "data": result
                })
                
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                
                display_investigation_result(result)
                
                # Additional options
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💬 Ask Follow-up Questions", use_container_width=True):
                        st.session_state.current_mode = "chat"
                        st.rerun()
                with col2:
                    if st.button("🔄 Investigate Another Claim", use_container_width=True):
                        st.session_state.investigation_results = None
                        st.rerun()
            else:
                error_msg = f"Investigation failed: {response.status_code}"
                st.error(f"❌ {error_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {str(e)}")
        except requests.RequestException as e:
            st.error(f"❌ API Connection Error: {str(e)}")
        
        st.rerun()

# ==================== FOOTER ====================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption(
    "🔒 ClaimPilot AI | Secure Insurance Intelligence | "
    "Status: "
    f"{'🟢 Online' if st.session_state.api_status == 'online' else '🔴 Offline' if st.session_state.api_status == 'offline' else '⚠️ Error'}"
)

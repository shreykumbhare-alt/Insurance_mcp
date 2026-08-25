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
    page_title="ClaimPilot | Investigation Desk",
    page_icon="CP",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
    :root { --ink: #17211f; --muted: #6d7975; --paper: #f5f7f2; --line: #dbe2d9; --mint: #c9f2dc; --coral: #ef725f; }
    .stApp { background: radial-gradient(circle at 92% 0%, #e4f4e8 0, var(--paper) 24rem); color: var(--ink); }
    [data-testid="stSidebar"] { background: #17211f; }
    [data-testid="stSidebar"] * { color: #eef6ef; }
    [data-testid="stSidebar"] .stCaption { color: #aabcb2; }
    h1, h2, h3, p, label, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { font-family: 'Manrope', sans-serif; }
    h1 { letter-spacing: 0; font-size: 2.55rem; font-weight: 800; margin-bottom: 0.15rem; }
    h2 { letter-spacing: 0; font-weight: 800; }
    .eyebrow { color: var(--coral); font-family: 'DM Mono', monospace; font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; }
    .lede { color: var(--muted); font-size: 1.02rem; margin-top: 0; }
    .section-rule { border-top: 1px solid var(--line); margin: 1.3rem 0 1.1rem; }
    .status-pill { display: inline-block; border: 1px solid #afd7bd; background: var(--mint); color: #145338; border-radius: 999px; padding: .25rem .65rem; font: 500 .72rem 'DM Mono', monospace; }
    div[data-testid="stMetric"] { background: rgba(255,255,255,.9); border: 1px solid var(--line); border-radius: 8px; padding: 1rem 1.1rem; box-shadow: 0 4px 14px rgba(23,33,31,.04); }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--ink); font-weight: 800; }
    div[data-testid="stForm"] { background: rgba(255,255,255,.9); border: 1px solid var(--line); border-radius: 8px; padding: 1.2rem; box-shadow: 0 4px 14px rgba(23,33,31,.04); }
    .result-block { background: #ffffff; border-left: 4px solid var(--coral); border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin: .65rem 0 1rem; }
    .result-block h4 { font: 800 1rem 'Manrope', sans-serif; margin: 0 0 .35rem; }
    .mono { font-family: 'DM Mono', monospace; }
    .stButton button, .stFormSubmitButton button { min-height: 2.75rem; border-radius: 6px; border: 1px solid #b8c9bd; font-family: 'Manrope', sans-serif; font-weight: 800; transition: background .18s ease, border-color .18s ease, transform .18s ease, box-shadow .18s ease; }
    .stButton button:hover, .stFormSubmitButton button:hover { border-color: #24704c; box-shadow: 0 5px 12px rgba(36,112,76,.16); transform: translateY(-1px); }
    .stButton button:focus-visible, .stFormSubmitButton button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 3px solid rgba(239,114,95,.45) !important; outline-offset: 2px; }
    .stFormSubmitButton button[kind="primary"] { background: #24704c; border-color: #24704c; color: #ffffff; }
    .stFormSubmitButton button[kind="primary"]:hover { background: #18583a; border-color: #18583a; }
    input, textarea, [data-baseweb="select"] > div { border-radius: 6px !important; border-color: #cbd8ce !important; background: #ffffff !important; }
    input:hover, textarea:hover, [data-baseweb="select"] > div:hover { border-color: #82a691 !important; }
    label { color: #40514a !important; font-weight: 700 !important; }
    button[role="tab"] { color: var(--muted); font-family: 'Manrope', sans-serif; font-weight: 800; }
    button[role="tab"][aria-selected="true"] { color: #18583a; }
    [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 6px; background: rgba(255,255,255,.65); }
    [data-testid="stExpander"] summary:hover { color: #18583a; }
    @media (max-width: 700px) {
        h1 { font-size: 2rem; }
        div[data-testid="stForm"] { padding: .9rem; }
        .stButton button, .stFormSubmitButton button { width: 100%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_claims():
    if not DATASET_PATH.exists():
        return []
    with DATASET_PATH.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def coerce_claim_values(claim):
    numeric_fields = {
        "claim_amount", "customer_tenure", "claims_last_12m", "avg_hist_claim",
        "submission_delay", "previously_rejected_claims", "deviation_from_peer_claims",
    }
    result = {}
    for key, value in claim.items():
        if key == "is_fraud":
            continue
        if key in numeric_fields:
            result[key] = float(value) if "." in str(value) else int(value)
        else:
            result[key] = value
    return result


def api_request(api_url, path, payload):
    return requests.post(f"{api_url.rstrip('/')}{path}", json=payload, timeout=180)


def show_policies(policies):
    if not policies:
        st.caption("No policy references were returned.")
        return
    for policy in policies:
        if isinstance(policy, dict):
            title = policy.get("title", "Policy reference")
            content = policy.get("content", json.dumps(policy, indent=2))
            with st.expander(title):
                st.write(content)
        else:
            st.write(policy)


def show_investigation(result):
    triage = result.get("triage") or {}
    score = triage.get("fraud_score")
    risk_level = triage.get("risk_level") or "Unknown"
    action = triage.get("triage_action") or "No recommendation"

    st.markdown('<div class="eyebrow">Investigation complete</div>', unsafe_allow_html=True)
    st.subheader(f"Claim {result.get('claim_id', '')}")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Fraud score", f"{score:.2f}" if isinstance(score, (int, float)) else "N/A")
    metric_cols[1].metric("Risk tier", risk_level)
    metric_cols[2].metric("Recommended action", action)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="result-block"><h4>Risk analysis</h4></div>', unsafe_allow_html=True)
        st.write(result.get("risk_analysis") or "No analysis returned.")
        st.markdown('<div class="result-block"><h4>Investigator action plan</h4></div>', unsafe_allow_html=True)
        st.write(result.get("final_report") or "No final report returned.")
    with right:
        st.markdown('<div class="result-block"><h4>Triggered signals</h4></div>', unsafe_allow_html=True)
        signals = triage.get("signals") or {}
        if signals:
            for signal, triggered in signals.items():
                st.write(f"{'[x]' if triggered else '[ ]'} {signal.replace('_', ' ').title()}")
        else:
            st.caption("No risk signals returned.")
        st.markdown('<div class="result-block"><h4>Policy and case context</h4></div>', unsafe_allow_html=True)
        show_policies(result.get("policy_matches"))


claims = load_claims()
with st.sidebar:
    st.markdown("# ClaimPilot")
    st.caption("Investigation desk")
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    api_url = st.text_input("API server", value=DEFAULT_API_URL)
    try:
        health = requests.get(f"{api_url.rstrip('/')}/health", timeout=2)
        st.markdown('<span class="status-pill">API online</span>', unsafe_allow_html=True) if health.ok else st.warning("API returned an error")
    except requests.RequestException:
        st.markdown('<span class="status-pill" style="background:#ffe0da;border-color:#f3afa2;color:#8e3024">API offline</span>', unsafe_allow_html=True)
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.caption("A human review surface for the multi-agent insurance workflow.")

st.markdown('<div class="eyebrow">Insurance intelligence / 01</div>', unsafe_allow_html=True)
st.title("Investigation desk")
st.markdown('<p class="lede">Run a claim through triage, risk analysis, and policy review, or ask the policy assistant a direct question.</p>', unsafe_allow_html=True)

investigate_tab, policy_tab = st.tabs(["Investigate a claim", "Ask policy assistant"])

with investigate_tab:
    if not claims:
        st.warning("The claim dataset could not be found. Enter a claim manually below.")
        selected_claim = {}
    else:
        claim_labels = [f"{claim['claim_id']}  |  {claim['claim_type']}  |  ${float(claim['claim_amount']):,.2f}" for claim in claims]
        selected_index = st.selectbox("Load a claim from the dataset", range(len(claims)), format_func=lambda index: claim_labels[index])
        selected_claim = claims[selected_index]

    default_claim = json.dumps(coerce_claim_values(selected_claim), indent=2)
    with st.form("investigation_form"):
        claim_id = st.text_input("Claim ID", value=selected_claim.get("claim_id", "CLM_NEW"))
        claim_json = st.text_area("Claim details (JSON)", value=default_claim, height=250)
        submitted = st.form_submit_button("Run investigation", type="primary", use_container_width=True)

    if submitted:
        try:
            claim_data = json.loads(claim_json)
            if not isinstance(claim_data, dict):
                raise ValueError("Claim details must be a JSON object.")
            with st.spinner("Running the investigation graph..."):
                response = api_request(api_url, "/api/v1/investigate", {"claim_id": claim_id, "raw_claim_data": claim_data})
            if response.ok:
                st.session_state["investigation_result"] = response.json()
            else:
                st.error(f"Investigation failed ({response.status_code}): {response.text}")
        except json.JSONDecodeError as error:
            st.error(f"Invalid JSON: {error}")
        except requests.RequestException as error:
            st.error(f"Could not reach the API: {error}")

    if st.session_state.get("investigation_result"):
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
        show_investigation(st.session_state["investigation_result"])

with policy_tab:
    st.markdown("Ask about coverage, deductibles, rules, or standard operating procedures.")
    with st.form("policy_form"):
        category = st.selectbox("Policy category", ["Auto", "Property", "Health"])
        question = st.text_area("Your question", placeholder="Is a delayed claim submission covered under this policy?", height=130)
        ask_submitted = st.form_submit_button("Ask assistant", type="primary", use_container_width=True)

    if ask_submitted:
        if not question.strip():
            st.error("Enter a question first.")
        else:
            try:
                with st.spinner("Searching policy context and drafting an answer..."):
                    response = api_request(api_url, "/api/v1/ask", {"question": question, "category": category})
                if response.ok:
                    st.session_state["policy_result"] = response.json()
                else:
                    st.error(f"Question failed ({response.status_code}): {response.text}")
            except requests.RequestException as error:
                st.error(f"Could not reach the API: {error}")

    if st.session_state.get("policy_result"):
        result = st.session_state["policy_result"]
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Policy assistant</div>', unsafe_allow_html=True)
        st.subheader("Answer")
        st.write(result.get("answer") or "No answer returned.")
        st.markdown('<div class="result-block"><h4>Sources</h4></div>', unsafe_allow_html=True)
        show_policies(result.get("policy_matches"))

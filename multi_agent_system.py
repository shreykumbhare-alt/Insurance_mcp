import asyncio
import json

from fastmcp import Client
from langgraph.graph import StateGraph, START, END

from state import ClaimState
from llm_factory import get_llm

# Initialize LLM
llm = get_llm(temperature=0.2)

# --- MCP Tool Helpers ---
# Unpacking Helper for FastMCP CallToolResult objects
def unpack_mcp_result(result):
    """Extracts dict/structured data from a FastMCP CallToolResult."""
    # 1. FastMCP structured data property
    if hasattr(result, "data") and result.data is not None:
        return result.data
    
    # 2. Extract from content blocks if .data is None
    if hasattr(result, "content") and result.content:
        raw_text = result.content[0].text
        if isinstance(raw_text, str):
            try:
                return json.loads(raw_text)
            except (json.JSONDecodeError, TypeError):
                return raw_text
        return raw_text
        
    return result


async def call_predictive_model_mcp(claim_data: dict) -> dict:
    """Connects to Predictive Model MCP Server."""
    async with Client("mcp_model_server.py") as mcp_client:
        res = await mcp_client.call_tool("predict_fraud_risk", arguments=claim_data)
        return unpack_mcp_result(res)

def supervisor_node(state: ClaimState) -> dict:
    """Single supervisor that decides the route once and finalizes once."""
    phase = state.get("phase")
    route = state.get("route")

    # Finalize only after the specialist has produced evidence.
    if phase == "finalize" or state.get("finalized"):
        if route == "policy_qa":
            # For policy QA, return just the answer without fraud investigation synthesis.
            answer = state.get("policy_answer", "No policy answer available.")
            return {
                "final_investigation_report": answer,
                "phase": "done",
                "finalized": True,
                "route": None,
            }

        # For claims triage/fraud investigation, synthesize a full fraud report.
        fraud_score = state.get("fraud_score", "N/A")
        risk_level = state.get("risk_level", "N/A")
        triage_action = state.get("triage_action", "N/A")
        is_fraud = state.get("is_fraud")
        fraud_reason = state.get("fraud_reason", "No specific fraud explanation was generated.")
        triggered_factors = state.get("triggered_factors", [])
        risk_summary = state.get("risk_analysis_summary", "No fraud analysis available.")
        policy_context = state.get("retrieved_policies", [])

        verdict_text = "FRAUD" if is_fraud else "NOT FRAUD"

        prompt = f"""
        You are the senior insurance supervisor.
        Synthesize a final Fraud Investigation Report for Claim ID {state.get('claim_id', 'UNKNOWN')}.

        Required outcome:
        - First sentence must clearly say: 'VERDICT: {verdict_text}.'
        - If the claim is fraud, explain exactly why using the triggering parameters and the model reason.
        - Use the following evidence: 
            1. TRIAGE SUMMARY: Score={fraud_score}, Tier={risk_level}, Action={triage_action}
            2. MODEL VERDICT: {is_fraud}
            3. MODEL FRAUD REASON: {fraud_reason}
            4. TRIGGERED FACTORS: {triggered_factors}
            5. RISK ANALYSIS: {risk_summary}
            6. POLICY & CASE CONTEXT: {policy_context}

        Format as 3 short, decisive bullets:
        - Bullet 1: verdict and reason
        - Bullet 2: the exact suspicious parameters that caused the decision
        - Bullet 3: recommended investigator action
        """
        response = llm.invoke(prompt)
        final_report = response.content if hasattr(response, 'content') else str(response)
        return {"final_investigation_report": final_report, "phase": "done", "finalized": True, "route": None}

    # Initial routing step: choose the specialist, but never leave a stale route behind.
    user_query = state.get("user_query", "") or ""
    raw_claim_data = state.get("raw_claim_data") or {}
    normalized_query = user_query.strip().lower()

    # Deterministic direct-answer guard: no claim payload means this is a policy question.
    if not raw_claim_data or raw_claim_data == {}:
        return {"route": "policy_qa", "phase": "route_selected", "finalized": False}

    # Short greetings should never trigger RAG or fraud-model investigation.
    if normalized_query in {"hello", "hi", "hey", "hello there", "hi there", "good morning", "good afternoon", "good evening"}:
        return {"route": "policy_qa", "phase": "route_selected", "finalized": False}

    prompt = f"""
    You are the senior insurance supervisor.
    Decide which specialist should handle this request.

    Rules:
    - Return exactly 'policy_qa' for policy, coverage, deductible, SOP, or compliance questions.
    - Return exactly 'claims_triage' for actual claim investigations or fraud-risk assessment jobs.

    Inputs:
    - User query: {user_query}
    - Claim payload: {raw_claim_data}

    Return only one word: 'policy_qa' or 'claims_triage'.
    """

    try:
        decision = llm.invoke(prompt)
        chosen_route = decision.content.strip().lower() if hasattr(decision, 'content') else str(decision).strip().lower()
    except Exception:
        chosen_route = "claims_triage"

    if "policy" in chosen_route:
        return {"route": "policy_qa", "phase": "route_selected", "finalized": False}
    return {"route": "claims_triage", "phase": "route_selected", "finalized": False}


# --- Agent: General Policy QA (For Normal Questions) ---
async def general_policy_qa_node(state: ClaimState) -> dict:
    query = state.get("user_query", "General insurance policy query")
    category = state.get("raw_claim_data", {}).get("claim_type", "Auto") if state.get("raw_claim_data") else "Auto"
    normalized_query = str(query).strip().lower()

    if normalized_query in {"hello", "hi", "hey", "hello there", "hi there", "good morning", "good afternoon", "good evening"}:
        return {
            "retrieved_policies": [],
            "policy_answer": "Hello! How can I assist you today?",
            "phase": "finalize",
        }

    rag_res = await call_rag_retrieval_mcp(query, category)
    docs = rag_res.get("retrieved_chunks", [])

    context_text = "\n\n".join([f"[{d['title']}]: {d['content']}" for d in docs])

    prompt = f"""
    You are a helpful Insurance Customer Support Assistant.
    Answer the user's question clearly and concisely using only the provided policy context.

    User Query: {query}

    Relevant Policy Context:
    {context_text}
    """

    res = llm.invoke(prompt)
    answer = res.content if hasattr(res, 'content') else str(res)

    return {
        "retrieved_policies": docs,
        "policy_answer": answer,
        "phase": "finalize",
    }

async def call_rag_retrieval_mcp(query: str, category: str) -> dict:
    """Connects to RAG Retrieval MCP Server."""
    async with Client("mcp_rag_server.py") as mcp_client:
        res = await mcp_client.call_tool(
            "search_policy_and_cases", 
            arguments={"query": query, "category": category}
        )
        return unpack_mcp_result(res)

# --- Node 1: Claims Triage Agent ---
async def claims_triage_node(state: ClaimState) -> dict:
    print("\n[Node 1] Running Claims Triage Agent...")
    mcp_response = await call_predictive_model_mcp(state["raw_claim_data"])
    
    return {
        "fraud_score": mcp_response.get("fraud_score"),
        "risk_level": mcp_response.get("risk_level"),
        "triage_action": mcp_response.get("recommended_action"),
        "risk_signals": mcp_response.get("signals", {}),
        "is_fraud": mcp_response.get("is_fraud"),
        "fraud_reason": mcp_response.get("fraud_reason"),
        "triggered_factors": mcp_response.get("triggered_factors", []),
        "phase": "risk_analysis",
    }


# --- Node 2: Risk Analysis Agent ---
def risk_analysis_node(state: ClaimState) -> dict:
    print("[Node 2] Running Risk Analysis Agent...")
    
    prompt = f"""
    You are an expert Insurance Fraud Analyst. Determine the final fraud verdict and explain the exact drivers.
    - Fraud Score: {state['fraud_score']} ({state['risk_level']} Risk)
    - Fraud Verdict: {'FRAUD' if state.get('is_fraud') else 'NOT FRAUD'}
    - Raw Claim Details: {state['raw_claim_data']}
    - Risk Flags Triggered: {state['risk_signals']}
    - Triggered Fraud Factors: {state.get('triggered_factors', [])}
    - Existing Model Explanation: {state.get('fraud_reason', 'No specific explanation provided.')}

    Give a brief but decisive answer that states whether the claim is fraudulent or not, then explain why using the specific parameters that caused the outcome.
    """
    
    response = llm.invoke(prompt)
    analysis_text = response.content if hasattr(response, 'content') else str(response)
    
    return {"risk_analysis_summary": analysis_text, "phase": "policy_check"}


# --- Node 3: Policy Agent (RAG) ---
async def policy_agent_node(state: ClaimState) -> dict:
    print("[Node 3] Running Policy & Compliance Agent (RAG)...")
    
    # Construct targeted search query from the claim and the analyst's findings.
    search_query = (
        f"Fraud guidelines for {state['raw_claim_data'].get('claim_type')} claim; "
        f"submission delay, provider rules, and these risk findings: "
        f"{state.get('risk_analysis_summary', '')}"
    )
    category = state['raw_claim_data'].get('claim_type', 'Auto')
    
    rag_response = await call_rag_retrieval_mcp(search_query, category)
    retrieved_docs = rag_response.get("retrieved_chunks", [])
    
    return {"retrieved_policies": retrieved_docs, "phase": "finalize"}


# --- Build LangGraph Pipeline ---
def build_claim_investigation_graph():
    workflow = StateGraph(ClaimState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("policy_qa", general_policy_qa_node)
    workflow.add_node("claims_triage", claims_triage_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("policy_rag", policy_agent_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: (
            "END"
            if state.get("phase") in {"done", "finalize"} or state.get("finalized")
            else state.get("route", "claims_triage")
        ),
        {
            "END": END,
            "policy_qa": "policy_qa",
            "claims_triage": "claims_triage",
        },
    )
    workflow.add_edge("policy_qa", "supervisor")
    workflow.add_edge("claims_triage", "risk_analysis")
    workflow.add_edge("risk_analysis", "policy_rag")
    workflow.add_edge("policy_rag", "supervisor")

    return workflow.compile()


# --- Execution Test ---
if __name__ == "__main__":
    app = build_claim_investigation_graph()
    
    sample_input = {
        "claim_id": "CLM_99012",
        "raw_claim_data": {
            "claim_amount": 14500.0,
            "claim_type": "Auto",
            "customer_tenure": 2,
            "claims_last_12m": 3,
            "avg_hist_claim": 2100.0,
            "provider_id": "PRV_120",
            "geography": "Urban",
            "submission_delay": 50,
            "previously_rejected_claims": 1,
            "deviation_from_peer_claims": 6200.0
        }
    }
    
    result = asyncio.run(app.ainvoke(sample_input))
    print("\n" + "="*50)
    print("FINAL INVESTIGATION REPORT:")
    print("="*50)
    print(result["final_investigation_report"])
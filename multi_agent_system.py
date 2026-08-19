import asyncio
from fastmcp import Client
from langgraph.graph import StateGraph, START, END
from state import ClaimState
from llm_factory import get_llm
import json
from fastmcp import Client 

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

def intent_router_node(state: ClaimState) -> dict:
    user_query = state.get("user_query")
    raw_data = state.get("raw_claim_data")
    
    # If structured claim payload is provided without a prompt, default to investigation
    if raw_data and not user_query:
        return {"intent": "claim_investigation"}
    
    prompt = f"""
    Classify the following user request into exactly one of two categories:
    - 'policy_question': The user is asking a general question about policy coverage, rules, SOPs, or deductibles.
    - 'claim_investigation': The user wants to run a full fraud risk assessment on a specific claim dataset.

    User Input: "{user_query}"
    Return ONLY the exact string 'policy_question' or 'claim_investigation'. Do not include extra text.
    """
    
    res = llm.invoke(prompt)
    intent = res.content.strip().lower() if hasattr(res, 'content') else str(res).strip().lower()
    
    if "policy" in intent:
        return {"intent": "policy_question"}
    return {"intent": "claim_investigation"}

# --- Node: General Policy QA Agent (For Normal Doubts) ---
async def general_policy_qa_node(state: ClaimState) -> dict:
    query = state.get("user_query", "General insurance policy query")
    category = state.get("raw_claim_data", {}).get("claim_type", "Auto") if state.get("raw_claim_data") else "Auto"
    
    # Fetch relevant chunks from Weaviate RAG MCP
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
        "final_investigation_report": answer
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
        "risk_signals": mcp_response.get("signals", {})
    }


# --- Node 2: Risk Analysis Agent ---
def risk_analysis_node(state: ClaimState) -> dict:
    print("[Node 2] Running Risk Analysis Agent...")
    
    prompt = f"""
    You are an expert Insurance Fraud Analyst. Analyze the following model output and claim signals:
    - Fraud Score: {state['fraud_score']} ({state['risk_level']} Risk)
    - Raw Claim Details: {state['raw_claim_data']}
    - Risk Flags Triggered: {state['risk_signals']}
    
    Provide a concise explanation of WHY this claim was flagged and highlight specific suspicious anomalies.
    """
    
    response = llm.invoke(prompt)
    analysis_text = response.content if hasattr(response, 'content') else str(response)
    
    return {"risk_analysis_summary": analysis_text}


# --- Node 3: Policy Agent (RAG) ---
async def policy_agent_node(state: ClaimState) -> dict:
    print("[Node 3] Running Policy & Compliance Agent (RAG)...")
    
    # Construct targeted search query based on risk flags
    search_query = f"Fraud guidelines for {state['raw_claim_data'].get('claim_type')} submission delay or provider rules"
    category = state['raw_claim_data'].get('claim_type', 'Auto')
    
    rag_response = await call_rag_retrieval_mcp(search_query, category)
    retrieved_docs = rag_response.get("retrieved_chunks", [])
    
    return {"retrieved_policies": retrieved_docs}


# --- Node 4: Supervisor Agent ---
def supervisor_node(state: ClaimState) -> dict:
    print("[Node 4] Running Supervisor Node (Synthesizing Report)...")
    
    prompt = f"""
    Synthesize a final Fraud Investigation Report for Claim ID {state['claim_id']}:
    
    1. TRIAGE SUMMARY: Score={state['fraud_score']}, Tier={state['risk_level']}, Action={state['triage_action']}
    2. RISK ANALYSIS: {state['risk_analysis_summary']}
    3. POLICY & CASE CONTEXT: {state['retrieved_policies']}
    
    Format a clear 3-bullet action plan for the human investigator.
    """
    
    response = llm.invoke(prompt)
    final_report = response.content if hasattr(response, 'content') else str(response)
    
    return {"final_investigation_report": final_report}


# --- Build LangGraph Pipeline ---
def build_claim_investigation_graph():
    workflow = StateGraph(ClaimState)
    
    # Add Nodes
    workflow.add_node("claims_triage", claims_triage_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("policy_rag", policy_agent_node)
    workflow.add_node("supervisor", supervisor_node)
    
    # Add Directed Edges
    workflow.add_edge(START, "claims_triage")
    workflow.add_edge("claims_triage", "risk_analysis")
    workflow.add_edge("risk_analysis", "policy_rag")
    workflow.add_edge("policy_rag", "supervisor")
    workflow.add_edge("supervisor", END)
    
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
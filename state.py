from typing import TypedDict, List, Dict, Any, Optional

class ClaimState(TypedDict):
    claim_id: Optional[str]
    raw_claim_data: Dict[str, Any]
    user_query: Optional[str]
    intent: Optional[str]
    
    # Updated by Claims Triage Agent
    fraud_score: Optional[float]
    risk_level: Optional[str]
    triage_action: Optional[str]
    risk_signals: Optional[Dict[str, bool]]
    
    # Updated by Risk Analysis Agent
    risk_analysis_summary: Optional[str]
    
    # Updated by Policy Agent (RAG)
    retrieved_policies: Optional[List[Dict[str, Any]]]
    
    # Final Output from Supervisor
    final_investigation_report: Optional[str]
from typing import TypedDict, List, Dict, Any, Optional

class ClaimState(TypedDict):
    claim_id: Optional[str]
    raw_claim_data: Dict[str, Any]
    user_query: Optional[str]
    route: Optional[str]
    phase: Optional[str]
    finalized: Optional[bool]

    # Updated by Claims Triage Agent
    fraud_score: Optional[float]
    risk_level: Optional[str]
    triage_action: Optional[str]
    risk_signals: Optional[Dict[str, bool]]
    is_fraud: Optional[bool]
    fraud_reason: Optional[str]
    triggered_factors: Optional[list]

    # Updated by Risk Analysis Agent
    risk_analysis_summary: Optional[str]

    # Updated by Policy Agent (RAG)
    retrieved_policies: Optional[List[Dict[str, Any]]]
    policy_answer: Optional[str]

    # Final Output from Supervisor
    final_investigation_report: Optional[str]
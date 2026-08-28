import json
import os
from datetime import datetime, timezone

# Expanded knowledge base documents
documents = [
    {
        "doc_id": "DOC_POL_001",
        "doc_type": "policy_rules",
        "category": "Health",
        "title": "Health Policy Exclusion Guidelines",
        "content": "Pre-existing conditions treatments rendered within 90 days of policy creation are excluded. Delayed submissions exceeding 30 days require SIU fraud investigation.",
        "jurisdiction": "National"
    },
    {
        "doc_id": "DOC_SOP_002",
        "doc_type": "internal_sop",
        "category": "Auto",
        "title": "Auto Fraud Triaging SOP",
        "content": "Claims exceeding peer average by $3000 or filed past 45 days must be flagged for manual risk audit and provider frequency verification.",
        "jurisdiction": "National"
    },
    {
        "doc_id": "DOC_CASE_003",
        "doc_type": "historical_case",
        "category": "Auto",
        "title": "Historical Case PRV_120 Audit",
        "content": "Provider PRV_120 was convicted of inflating auto repair costs. Any claim linked to PRV_120 with deviation > $2000 should be escalated to SIU.",
        "jurisdiction": "Urban"
    },
    # --- New Knowledge Base Entries ---
    {
        "doc_id": "DOC_POL_004",
        "doc_type": "policy_rules",
        "category": "Property",
        "title": "Property & Casualty Water Damage Limitations",
        "content": "Gradual water leaks occurring over a period of 14 days or longer are excluded from coverage. Sudden and accidental pipe bursts remain fully covered up to the policy sub-limit of $50,000.",
        "jurisdiction": "National"
    },
    {
        "doc_id": "DOC_SOP_005",
        "doc_type": "internal_sop",
        "category": "Workers_Comp",
        "title": "Workers Compensation First Notice of Loss (FNOL) Protocol",
        "content": "Workplace injuries reported more than 7 business days post-incident require mandatory supervisor statements and payroll record verification before medical clearance payout.",
        "jurisdiction": "Statewide"
    },
    {
        "doc_id": "DOC_REG_006",
        "doc_type": "regulatory_bulletin",
        "category": "Life",
        "title": "Contestability Period Statutory Limits",
        "content": "Under State Insurance Code Sec. 402, life insurance policies passing the 2-year contestability window cannot be denied based on material misrepresentations made during application, except in cases of deliberate fraud.",
        "jurisdiction": "Statewide"
    },
    {
        "doc_id": "DOC_CASE_007",
        "doc_type": "historical_case",
        "category": "Property",
        "title": "Commercial Fire Claim Fraud Pattern - Precedent 2023-88",
        "content": "Claims involving commercial fire losses where inventory values spike > 200% within 60 days of policy inception require immediate forensic accounting audit and origin investigation.",
        "jurisdiction": "National"
    },
    {
        "doc_id": "DOC_UW_008",
        "doc_type": "underwriting_guide",
        "category": "Cyber",
        "title": "Cyber Liability Risk Assessment Standards",
        "content": "Applicants without Multi-Factor Authentication (MFA) enabled across all remote access points must be declined or surcharged a minimum 40% premium penalty.",
        "jurisdiction": "Global"
    },
    {
        "doc_id": "DOC_SOP_009",
        "doc_type": "internal_sop",
        "category": "General_Liability",
        "title": "Slip-and-Fall Claim Investigation Checklist",
        "content": "Any commercial general liability slip-and-fall claim lacking surveillance footage within 24 hours of incident must trigger a field investigator dispatch and weather history audit.",
        "jurisdiction": "Urban"
    },
    {
        "doc_id": "DOC_POL_010",
        "doc_type": "policy_rules",
        "category": "Health",
        "title": "Out-of-Network Emergency Care Reimbursement",
        "content": "Emergency medical treatment obtained out-of-network is reimbursed at in-network rates if the distance to the nearest network facility exceeded 25 miles at the time of the event.",
        "jurisdiction": "National"
    }
]

os.makedirs("cloud_storage_json", exist_ok=True)

# Using timezone-aware UTC datetime for current best practices
for doc in documents:
    doc["processed_at"] = datetime.now(timezone.utc).isoformat()
    filepath = f"cloud_storage_json/{doc['doc_id']}.json"
    with open(filepath, "w") as f:
        json.dump(doc, f, indent=2)

print(f"Successfully saved {len(documents)} JSON chunks to './cloud_storage_json/'")
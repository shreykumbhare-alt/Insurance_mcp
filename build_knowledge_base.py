import json
import os
from datetime import datetime

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
    }
]

os.makedirs("cloud_storage_json", exist_ok=True)
for doc in documents:
    doc["processed_at"] = datetime.utcnow().isoformat()
    filepath = f"cloud_storage_json/{doc['doc_id']}.json"
    with open(filepath, "w") as f:
        json.dump(doc, f, indent=2)

print("Saved JSON chunks with metadata to './cloud_storage_json/'")
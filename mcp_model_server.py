import os
import json
import joblib
import numpy as np
import pandas as pd
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Insurance Fraud Prediction Server")

# Global variables for model artifacts
MODEL = None
ENCODER = None
PROVIDER_COUNTS = None
METADATA = None


def load_artifacts():
    global MODEL, ENCODER, PROVIDER_COUNTS, METADATA
    if MODEL is None:
        model_dir = "models"
        if not os.path.exists(model_dir):
            raise FileNotFoundError(
                "Models directory not found. Please run 'train_model.py' first."
            )

        MODEL = joblib.load(os.path.join(model_dir, "fraud_model.joblib"))
        ENCODER = joblib.load(os.path.join(model_dir, "categorical_encoder.joblib"))
        PROVIDER_COUNTS = joblib.load(os.path.join(model_dir, "provider_counts.joblib"))
        with open(os.path.join(model_dir, "metadata.json"), "r") as f:
            METADATA = json.load(f)


@mcp.tool()
def predict_fraud_risk(
    claim_amount: float,
    claim_type: str,
    customer_tenure: int,
    claims_last_12m: int,
    avg_hist_claim: float,
    provider_id: str,
    geography: str,
    submission_delay: int,
    previously_rejected_claims: int,
    deviation_from_peer_claims: float,
) -> dict:
    """Calculates fraud probability and risk classification for an insurance claim.

    Args:
        claim_amount: Dollar value of current claim.
        claim_type: Type of policy claim ('Auto', 'Health', 'Property').
        customer_tenure: Customer policy tenure in months.
        claims_last_12m: Number of claims submitted in the last 12 months.
        avg_hist_claim: Historical average claim amount for this policyholder.
        provider_id: Unique identifier for healthcare provider / repair facility.
        geography: Region location ('Urban', 'Suburban', 'Rural').
        submission_delay: Delay in days between incident and claim filing.
        previously_rejected_claims: Count or binary flag of past rejected claims.
        deviation_from_peer_claims: Variance from regional or peer category mean.

    Returns:
        dict: High-level risk score, risk tier, and raw features summary.
    """
    load_artifacts()

    # 1. Feature Engineering
    provider_claim_freq = PROVIDER_COUNTS.get(provider_id, 1)

    num_features = [
        claim_amount,
        customer_tenure,
        claims_last_12m,
        avg_hist_claim,
        submission_delay,
        previously_rejected_claims,
        deviation_from_peer_claims,
        provider_claim_freq,
    ]

    # 2. Categorical Encoding
    cat_df = pd.DataFrame([[claim_type, geography]], columns=METADATA["categorical_cols"])
    cat_encoded = ENCODER.transform(cat_df)

    # 3. Combine Features
    X_input = np.hstack([np.array(num_features).reshape(1, -1), cat_encoded])

    # 4. Predict
    fraud_probability = float(MODEL.predict_proba(X_input)[0][1])

    # 5. Risk Categorization
    if fraud_probability >= 0.70:
        risk_level = "HIGH"
        recommended_action = "ESCALATE_TO_SIU"
    elif fraud_probability >= 0.35:
        risk_level = "MEDIUM"
        recommended_action = "REQUEST_FURTHER_DOCUMENTATION"
    else:
        risk_level = "LOW"
        recommended_action = "AUTO_APPROVE"

    return {
        "status": "success",
        "fraud_score": round(fraud_probability, 4),
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "signals": {
            "high_delay_flag": submission_delay > 30,
            "peer_deviation_flag": deviation_from_peer_claims > 2000,
            "frequent_claimant_flag": claims_last_12m > 2,
        },
    }


if __name__ == "__main__":
    # Start the FastMCP server over stdio or HTTP
    mcp.run()
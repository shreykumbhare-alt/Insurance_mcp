from mcp_model_server import predict_fraud_risk


def test_predict_fraud_risk_returns_verdict_and_reasons():
    result = predict_fraud_risk(
        claim_amount=14500.0,
        claim_type="Auto",
        customer_tenure=2,
        claims_last_12m=3,
        avg_hist_claim=2100.0,
        provider_id="PRV_120",
        geography="Urban",
        submission_delay=50,
        previously_rejected_claims=1,
        deviation_from_peer_claims=6200.0,
    )

    assert "is_fraud" in result
    assert isinstance(result["is_fraud"], bool)
    assert "fraud_reason" in result
    assert isinstance(result["fraud_reason"], str)
    assert "triggered_factors" in result
    assert isinstance(result["triggered_factors"], list)
    assert result["triggered_factors"]

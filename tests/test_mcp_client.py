# test_mcp_client.py
import asyncio
from fastmcp import Client

client = Client("mcp_model_server.py")  # connects via stdio process transport


async def test_inference():
    async with client:
        result = await client.call_tool(
            "predict_fraud_risk",
            arguments={
                "claim_amount": 12500.0,
                "claim_type": "Auto",
                "customer_tenure": 3,
                "claims_last_12m": 3,
                "avg_hist_claim": 2000.0,
                "provider_id": "PRV_120",
                "geography": "Urban",
                "submission_delay": 45,
                "previously_rejected_claims": 1,
                "deviation_from_peer_claims": 5500.0,
            },
        )
        print("MCP Server Response:\n", result)


if __name__ == "__main__":
    asyncio.run(test_inference())
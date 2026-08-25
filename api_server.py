from contextlib import asynccontextmanager
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from multi_agent_system import build_claim_investigation_graph

# Terminal Color Formatter
class TerminalColors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class ClaimInput(BaseModel):
    claim_id: str
    raw_claim_data: dict


class QuestionInput(BaseModel):
    question: str
    category: str = "Auto"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and compile graph on startup
    app.state.graph_app = build_claim_investigation_graph()
    yield


app = FastAPI(
    title="Insurance Claim Investigation API",
    lifespan=lifespan,
)


def extract_data(obj):
    """Utility to unwrap CallToolResult, text content, or stringified tool outputs."""
    if obj is None:
        return {}

    # 1. Handle FastMCP CallToolResult .data attribute
    if hasattr(obj, "data") and obj.data is not None:
        return obj.data

    # 2. Handle object with .content block list (TextContent)
    if hasattr(obj, "content") and obj.content:
        first_block = obj.content[0]
        raw_text = getattr(first_block, "text", str(first_block))
        if isinstance(raw_text, str):
            try:
                return json.loads(raw_text)
            except (json.JSONDecodeError, TypeError):
                return raw_text
        return raw_text

    # 3. Handle raw string containing JSON
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except (json.JSONDecodeError, TypeError):
            return obj

    return obj


def log_agent_node_start(node_name: str):
    """Prints a styled header when an agent node begins execution."""
    print(f"\n{TerminalColors.CYAN}{'='*60}{TerminalColors.RESET}")
    print(
        f"{TerminalColors.BOLD}{TerminalColors.YELLOW}▶ AGENT EXECUTION:{TerminalColors.RESET} "
        f"{TerminalColors.MAGENTA}{TerminalColors.BOLD}[ {node_name.upper()} ]{TerminalColors.RESET}"
    )
    print(f"{TerminalColors.CYAN}{'='*60}{TerminalColors.RESET}")


def log_agent_node_output(node_name: str, node_update: dict):
    """Prints formatted output data for the agent in terminal."""
    print(
        f"{TerminalColors.GREEN}✔ Node completed:{TerminalColors.RESET} "
        f"{TerminalColors.BOLD}{node_name}{TerminalColors.RESET}"
    )
    print(f"{TerminalColors.BLUE}Output Payload:{TerminalColors.RESET}")

    # Pretty-print dictionary update
    try:
        formatted_json = json.dumps(node_update, indent=2, default=str)
        print(f"{TerminalColors.RESET}{formatted_json}")
    except Exception:
        print(f"{TerminalColors.RESET}{node_update}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Insurance Multi-Agent Flow"}


@app.post("/api/v1/investigate")
async def investigate_claim(payload: ClaimInput):
    """Trigger the LangGraph workflow and stream terminal execution updates."""
    try:
        sample_input = {
            "claim_id": payload.claim_id,
            "raw_claim_data": payload.raw_claim_data,
        }

        print(f"\n\n{TerminalColors.BOLD}{TerminalColors.GREEN}" f"🚀 STARTING AGENT WORKFLOW FOR CLAIM: {payload.claim_id}" f"{TerminalColors.RESET}")

        start_time = time.time()
        final_state = {}

        # Stream graph node transitions real-time using `astream`
        async for chunk in app.state.graph_app.astream(sample_input, stream_mode="updates"):
            # chunk format with stream_mode="updates" is {node_name: node_state_update}
            for node_name, node_update in chunk.items():
                log_agent_node_start(node_name)
                log_agent_node_output(node_name, node_update)

                # Collect aggregated state
                if isinstance(node_update, dict):
                    final_state.update(node_update)

        elapsed_time = round(time.time() - start_time, 2)
        print(f"\n{TerminalColors.BOLD}{TerminalColors.GREEN}" f"✅ WORKFLOW COMPLETE! (Elapsed: {elapsed_time}s)" f"{TerminalColors.RESET}\n")

        # Safely extract full state outputs
        return {
            "status": "success",
            "claim_id": final_state.get("claim_id", payload.claim_id),
            "triage": {
                "fraud_score": final_state.get("fraud_score"),
                "risk_level": final_state.get("risk_level"),
                "triage_action": final_state.get("triage_action"),
                "signals": final_state.get("risk_signals"),
            },
            "risk_analysis": final_state.get("risk_analysis_summary"),
            "policy_matches": extract_data(final_state.get("retrieved_policies")),
            "final_report": final_state.get("final_investigation_report"),
        }

    except Exception as e:
        print(f"\n{TerminalColors.BOLD}\033[91m❌ ERROR IN GRAPH FLOW: {str(e)}{TerminalColors.RESET}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ask")
async def ask_policy_question(payload: QuestionInput):
    """Run the graph's direct policy-question node with RAG-backed context."""
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")

    try:
        final_state = {}
        graph_input = {
            "claim_id": None,
            "raw_claim_data": {"claim_type": payload.category},
            "user_query": payload.question,
            "intent": "policy_question",
        }

        async for chunk in app.state.graph_app.astream(graph_input, stream_mode="updates"):
            for node_name, node_update in chunk.items():
                log_agent_node_start(node_name)
                log_agent_node_output(node_name, node_update)
                if isinstance(node_update, dict):
                    final_state.update(node_update)

        return {
            "status": "success",
            "question": payload.question,
            "policy_matches": extract_data(final_state.get("retrieved_policies")),
            "answer": final_state.get("final_investigation_report"),
        }
    except Exception as e:
        print(f"\n{TerminalColors.BOLD}\033[91mERROR IN QA GRAPH FLOW: {str(e)}{TerminalColors.RESET}\n")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
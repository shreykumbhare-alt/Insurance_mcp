# 🛡️ Intelligent Insurance Claims Risk & Investigation Assistant

An enterprise-grade, agentic AI platform designed to automate insurance fraud triage, policy verification, and risk analysis. The platform combines **Predictive Machine Learning (LightGBM)** with **Agentic RAG (Weaviate Vector DB)** using the **Model Context Protocol (MCP)**, orchestrated via **LangGraph** and monitored using **Langfuse**.

---

## 📐 System Architecture & Workflow

```mermaid
graph TD
    A[Client / Postman] -->|POST /api/v1/investigate| B(FastAPI Endpoint)
    
    subgraph Multi-Agent System [LangGraph Flow]
        B --> C[1. Claims Triage Agent]
        C --> D[2. Risk Analysis Agent]
        D --> E[3. Policy Agent - RAG]
        E --> F[4. Supervisor Node]
    end

    subgraph Tooling Layer
        C -->|MCP Tool| G[(Predictive ML Model Server)]
        E -->|MCP Tool| H[(Weaviate Vector DB Server)]
    end

    subgraph Telemetry
        Multi-Agent System -.->|Traces| I[Langfuse Observability]
    end

    F -->|JSON Output| B

# 🛡️ Intelligent Insurance Claims Risk & Investigation Assistant

An enterprise-grade, agentic AI platform designed to automate insurance fraud triage, policy verification, and risk analysis. The platform combines **Predictive Machine Learning (LightGBM)** with **Agentic RAG (Weaviate Vector DB)** using the **Model Context Protocol (MCP)**, orchestrated via **LangGraph** and monitored using **Langfuse**.

---

## 📐 System Architecture & Workflow

```mermaid
graph TD
    A[Client Request / Postman] -->|POST /api/v1/investigate| B(FastAPI Server)
    
    subgraph Multi-Agent System [LangGraph Orchestrator]
        B --> C[Claims Triage Agent]
        C --> D[Risk Analysis Agent]
        D --> E[Policy Agent - RAG]
        E --> F[Supervisor Agent]
    end

    subgraph MCP & Data Layer
        C -->|FastMCP Tool Call| G[(Predictive Model MCP\nLightGBM / Scikit-Learn)]
        E -->|FastMCP Tool Call| H[(RAG Retrieval MCP\nWeaviate Vector DB)]
    end

    subgraph Observability
        Multi-Agent System -.->|Traces & Metrics| I[Langfuse Platform]
    end

    F -->|Aggregated Report| B
    B -->|JSON Response| A

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px

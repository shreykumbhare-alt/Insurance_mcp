# 🛡️ Agentic Insurance Fraud Risk & Investigation System

An enterprise-grade, multi-agent AI system designed to detect, analyze, and investigate fraudulent insurance claims. This project combines tabular machine learning (LightGBM/XGBoost), agentic retrieval-augmented generation (RAG via Weaviate), Model Context Protocol (MCP) tool standardizations, and full-stack LLM observability via Langfuse.

---

## 📐 Architecture & System Flow

GitHub natively renders the Mermaid diagram below into an interactive architecture flowchart:

```mermaid
graph TD
    %% User/API Entry
    Client[📱 Client / Postman / UI] -->|POST /api/v1/investigate| API[🚀 FastAPI Web Server]
    
    subgraph LangGraph Multi-Agent Orchestrator
        API -->|Invoke Flow| Node1[1️⃣ Claims Triage Agent]
        Node1 -->|Fraud Score & Flags| Node2[2️⃣ Risk Analysis Agent]
        Node2 -->|Anomalies Identified| Node3[3️⃣ Policy Agent - RAG]
        Node3 -->|Policy & SOP Context| Node4[4️⃣ Supervisor Agent]
        Node4 -->|Synthesize Final Report| API
    end

    subgraph Model Context Protocol Services
        Node1 <-->|Stdio Call| MCP_ML[⚡ Model MCP Server]
        MCP_ML <-->|Load Artifacts| ML_Model[(🤖 LightGBM Classifier)]
        
        Node3 <-->|Stdio Call| MCP_RAG[🔍 Retrieval MCP Server]
        MCP_RAG <-->|Vector/Hybrid Search| VectorDB[(🐳 Weaviate Vector DB)]
    end

    subgraph Observability & Storage
        API -.->|Traces & Telemetry| Langfuse[📊 Langfuse Observability]
        VectorDB <-->|Load Chunks| Storage[📁 Local/Cloud JSON Storage]
    end

    style Client fill:#eceff1,stroke:#37474f,stroke-width:2px
    style API fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style Node1 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Node2 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Node3 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Node4 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style MCP_ML fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style MCP_RAG fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Langfuse fill:#fce4ec,stroke:#c2185b,stroke-width:2px

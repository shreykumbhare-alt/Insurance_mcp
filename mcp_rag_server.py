# mcp_rag_server.py
import weaviate
import weaviate.classes.query as wvq
from fastmcp import FastMCP
from sentence_transformers import SentenceTransformer

mcp = FastMCP("Insurance Policy RAG Server")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def ensure_collection_exists(client):
    """Ensures collection exists to prevent schema missing exceptions."""
    if not client.collections.exists("InsuranceKnowledgeBase"):
        print("⚠️ 'InsuranceKnowledgeBase' schema missing. Auto-creating...")
        import os, subprocess

        # Auto-trigger indexer script if available
        if os.path.exists("index_to_weaviate.py"):
            subprocess.run(["python", "index_to_weaviate.py"], check=True)


@mcp.tool()
def search_policy_and_cases(query: str, category: str = "Auto") -> dict:
    """Searches insurance policies, SOPs, and historical fraud cases matching query."""
    client = weaviate.connect_to_local(host="localhost", port=8080, grpc_port=50051)

    try:
        ensure_collection_exists(client)
        collection = client.collections.get("InsuranceKnowledgeBase")

        query_vector = embedder.encode(query).tolist()
        where_filter = (
            wvq.Filter.by_property("category").equal(category)
            if category
            else None
        )

        results = collection.query.near_vector(
            near_vector=query_vector, limit=3, filters=where_filter
        )

        snippets = [
            {
                "doc_id": obj.properties["doc_id"],
                "title": obj.properties["title"],
                "content": obj.properties["content"],
            }
            for obj in results.objects
        ]

        return {"status": "success", "retrieved_chunks": snippets}
    finally:
        client.close()


if __name__ == "__main__":
    mcp.run()
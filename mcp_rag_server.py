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


def diversify_results(objects, max_results=6):
    """Keep a broad mix of categories and document types instead of repeating similar hits."""
    selected = []
    seen_ids = set()
    by_category = {}
    by_type = {}

    for obj in objects:
        props = obj.properties
        doc_id = props.get("doc_id")
        if not doc_id or doc_id in seen_ids:
            continue

        category = props.get("category", "General")
        doc_type = props.get("doc_type", "general")

        by_category.setdefault(category, 0)
        by_type.setdefault(doc_type, 0)

        if len(selected) >= max_results:
            break

        selected.append({
            "doc_id": doc_id,
            "title": props.get("title"),
            "content": props.get("content"),
            "category": category,
            "doc_type": doc_type,
        })
        seen_ids.add(doc_id)
        by_category[category] += 1
        by_type[doc_type] += 1

    # Prefer more spread if more candidates are available.
    if len(selected) < max_results:
        for obj in objects:
            props = obj.properties
            doc_id = props.get("doc_id")
            if doc_id in seen_ids:
                continue
            selected.append({
                "doc_id": doc_id,
                "title": props.get("title"),
                "content": props.get("content"),
                "category": props.get("category", "General"),
                "doc_type": props.get("doc_type", "general"),
            })
            seen_ids.add(doc_id)
            if len(selected) >= max_results:
                break

    return selected


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
            if category and category.lower() != "general"
            else None
        )

        candidate_results = []
        for current_filter in [where_filter, None]:
            if current_filter is not None:
                results = collection.query.near_vector(
                    near_vector=query_vector,
                    limit=12,
                    filters=current_filter,
                )
            else:
                results = collection.query.near_vector(
                    near_vector=query_vector,
                    limit=12,
                )

            candidate_results.extend(results.objects)

        unique_hits = []
        seen = set()
        for obj in candidate_results:
            doc_id = obj.properties.get("doc_id")
            if doc_id and doc_id not in seen:
                unique_hits.append(obj)
                seen.add(doc_id)

        snippets = diversify_results(unique_hits, max_results=6)
        return {"status": "success", "retrieved_chunks": snippets}
    finally:
        client.close()


if __name__ == "__main__":
    mcp.run()
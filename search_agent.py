import weaviate
import weaviate.classes.query as wvq
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def query_rag_knowledge_base(user_query: str, category_filter: str = None):
    client = weaviate.connect_to_local(host="localhost", port=8080, grpc_port=50051)
    collection = client.collections.get("InsuranceKnowledgeBase")
    
    # 1. Embed incoming query
    query_vector = embedder.encode(user_query).tolist()
    
    # 2. Build metadata filter if specified
    where_filter = None
    if category_filter:
        where_filter = wvq.Filter.by_property("category").equal(category_filter)
        
    # 3. Perform Hybrid / Vector Search
    results = collection.query.near_vector(
        near_vector=query_vector,
        limit=2,
        filters=where_filter,
        return_metadata=wvq.MetadataQuery(distance=True)
    )
    
    formatted_results = []
    for obj in results.objects:
        formatted_results.append({
            "title": obj.properties["title"],
            "doc_type": obj.properties["doc_type"],
            "content": obj.properties["content"],
            "distance": round(obj.metadata.distance, 4)
        })
        
    client.close()
    return formatted_results

if __name__ == "__main__":
    print("Testing Search Query 1: 'What are the rules for delayed submission?'")
    res = query_rag_knowledge_base("delayed submission fraud rules", category_filter="Health")
    print(res)
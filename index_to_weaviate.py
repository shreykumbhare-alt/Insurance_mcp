import os
import json
import weaviate
import weaviate.classes.config as wvc
from sentence_transformers import SentenceTransformer

# 1. Connect to Local Weaviate Container
client = weaviate.connect_to_local(host="localhost", port=8080, grpc_port=50051)

print("Weaviate Ready:", client.is_ready())

# 2. Initialize Embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# 3. Create Collection (Schema)
collection_name = "InsuranceKnowledgeBase"

# Delete existing collection if re-running
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)

collection = client.collections.create(
    name=collection_name,
    vectorizer_config=wvc.Configure.Vectorizer.none(),  # We supply external embeddings
    properties=[
        wvc.Property(name="doc_id", data_type=wvc.DataType.TEXT),
        wvc.Property(name="doc_type", data_type=wvc.DataType.TEXT),
        wvc.Property(name="category", data_type=wvc.DataType.TEXT),
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="content", data_type=wvc.DataType.TEXT),
        wvc.Property(name="jurisdiction", data_type=wvc.DataType.TEXT),
    ]
)

# 4. Load JSON Chunks and Index with Vectors
json_folder = "cloud_storage_json"
data_objects = []

for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        with open(os.path.join(json_folder, filename), "r") as f:
            data = json.load(f)
            
            # Embed content string
            vector = embedder.encode(data["content"]).tolist()
            
            # Create Weaviate object
            collection.data.insert(
                properties={
                    "doc_id": data["doc_id"],
                    "doc_type": data["doc_type"],
                    "category": data["category"],
                    "title": data["title"],
                    "content": data["content"],
                    "jurisdiction": data["jurisdiction"],
                },
                vector=vector
            )

print(f"✅ Indexed {len(os.listdir(json_folder))} document chunks into Weaviate!")
client.close()
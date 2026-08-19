import os
import json

# Disable Torch dynamic compilation before imports
os.environ["TORCHINDUCTOR_DISABLE"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"

from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma

# 1. Load document with Docling
print("Loading PDF...")
loader = DoclingLoader(file_path="irda_health_insurance_policyholder_guidance.pdf")
raw_docs = loader.load()

# 2. Local Embedding Model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# 3. Semantic Chunking
print("Chunking semantically...")
text_splitter = SemanticChunker(embeddings)
chunks = text_splitter.split_documents(raw_docs)

# 4. Metadata Sanitizer for ChromaDB
def sanitize_metadata(documents):
    """Converts nested dicts/lists to JSON strings for ChromaDB compatibility."""
    for doc in documents:
        cleaned_meta = {}
        for key, value in doc.metadata.items():
            if isinstance(value, (dict, list)):
                cleaned_meta[key] = json.dumps(value)
            else:
                cleaned_meta[key] = value
        doc.metadata = cleaned_meta
    return documents

cleaned_chunks = sanitize_metadata(chunks)

# 5. Populate ChromaDB Vector Store
print("Building vector database...")
vectorstore = Chroma.from_documents(documents=cleaned_chunks, embedding=embeddings)

# 6. Query the Document
user_question = "What is health insurance?"
matching_chunks = vectorstore.similarity_search(user_question, k=2)

print(f"\n--- Answer Found in Document ({len(matching_chunks)} chunks retrieved) ---\n")
for i, doc in enumerate(matching_chunks):
    # Parse back the serialized JSON string safely
    dl_meta = json.loads(doc.metadata.get("dl_meta", "{}"))
    doc_items = dl_meta.get("doc_items", [{}])
    page_no = doc_items[0].get("prov", [{}])[0].get("page_no", "Unknown") if doc_items else "Unknown"

    print(f"--- Result {i+1} (Page {page_no}) ---")
    print(f"Content:\n{doc.page_content.strip()}\n")
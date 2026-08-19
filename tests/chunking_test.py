from langchain_docling import DoclingLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

pdf_path = "irda_health_insurance_policyholder_guidance.pdf"

# 1. Load using Docling (handles layout, tables, OCR, & text extraction)
print("Loading PDF with Docling...")
loader = DoclingLoader(file_path=pdf_path)
raw_docs = loader.load()

# 2. Initialize local HuggingFace embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# 3. Create Semantic Chunker
text_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90.0,
)

# 4. Chunk the document
chunks = text_splitter.split_documents(raw_docs)

print(f"\nTotal Chunks Created: {len(chunks)}\n")
for i, chunk in enumerate(chunks[:2]):
    print(f"--- Chunk {i+1} ---")
    print(f"Content:\n{chunk.page_content.strip()[:300]}...")
    print(f"\nMetadata: {chunk.metadata}\n")
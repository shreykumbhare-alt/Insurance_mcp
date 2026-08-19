from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# Sample Insurance Policy Document
SAMPLE_POLICY_DOC = """
# Health Insurance Policy - Policy ID: POL_HEALTH_2024

## Section 1: Coverage Rules
1.1 Inpatient Care: Covers up to $50,000 per policy year for emergency admissions.
1.2 Outpatient Care: Requires a $25 copay per visit with a maximum of 12 visits per calendar year.
1.3 Diagnostic Tests: Lab work and MRI scans are covered at 80% after deductible is met.

## Section 2: Fraud & Claim Exclusions
2.1 Pre-existing Conditions: Treatments related to unlisted pre-existing conditions within 90 days of policy start date are excluded.
2.2 Delayed Submission: Claims filed more than 30 days after the incident date are subject to mandatory SIU review.
2.3 Unregistered Providers: Claims for services rendered by non-accredited facilities will be automatically rejected.

## Section 3: Standard Operating Procedures (SOP)
3.1 Fast-Track Approval: Claims under $1,000 with clean history are eligible for automated approval.
3.2 Manual Investigation: Claims with high provider frequency (>15 claims/month) trigger immediate manual audit.
"""

def test_recursive_chunking(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_text(text)
    print(f"\n--- Recursive Character Chunking (Total: {len(chunks)}) ---")
    for i, c in enumerate(chunks):
        print(f"[Chunk {i+1}]:\n{c}\n")

def test_markdown_chunking(text: str):
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = markdown_splitter.split_text(text)
    print(f"\n--- Markdown Header Chunking (Total: {len(chunks)}) ---")
    for i, c in enumerate(chunks):
        print(f"[Chunk {i+1} Metadata]: {c.metadata}")
        print(f"[Chunk {i+1} Content]:\n{c.page_content}\n")

if __name__ == "__main__":
    test_recursive_chunking(SAMPLE_POLICY_DOC)
    # test_markdown_chunking(SAMPLE_POLICY_DOC)
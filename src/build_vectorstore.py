import pandas as pd
import pyarrow.parquet as pq
import chromadb
from chromadb.config import Settings
import numpy as np

print(" Building Vector Store from Pre-built Embeddings")
print("="*60)

# Load a sample of the data (1000 rows for testing)
print(" Loading complaint data...")
parquet_file = pq.ParquetFile('data/complaint_embeddings.parquet')

# Get sample
batches = []
for i, batch in enumerate(parquet_file.iter_batches(batch_size=1000)):
    batches.append(batch)
    if i >= 0:  # Just get first 1000 rows
        break

df = batches[0].to_pandas() if batches else pd.DataFrame()
print(f" Loaded {len(df)} complaint chunks")

# Initialize ChromaDB
print(" Initializing ChromaDB...")
client = chromadb.PersistentClient(
    path="vectorstore_final/",
    settings=Settings(allow_reset=True)
)

# Create collection
collection = client.get_or_create_collection(
    name="complaints_final",
    metadata={"hnsw:space": "cosine"}
)

# Add documents to vector store
print(" Adding documents to vector store...")

ids = []
documents = []
metadatas = []
embeddings = []

for i, row in df.iterrows():
    # Get data from row
    doc_id = row['id']
    doc_text = row['document']
    embedding = row['embedding']
    metadata = row['metadata']
    
    # Prepare metadata
    meta_dict = {
        'product_category': metadata.get('product_category', ''),
        'product': metadata.get('product', ''),
        'issue': metadata.get('issue', ''),
        'sub_issue': metadata.get('sub_issue', ''),
        'company': metadata.get('company', ''),
        'state': metadata.get('state', ''),
        'complaint_id': metadata.get('complaint_id', ''),
        'chunk_index': metadata.get('chunk_index', 0),
        'total_chunks': metadata.get('total_chunks', 1)
    }
    
    ids.append(doc_id)
    documents.append(str(doc_text))
    metadatas.append(meta_dict)
    embeddings.append(embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding))
    
    # Progress
    if (i + 1) % 100 == 0:
        print(f"  Processed {i+1}/{len(df)}...")

# Add to collection
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)

print(f" Vector store created with {collection.count()} documents")
print(" Saved to: vectorstore_final/")

# Test the vector store
print("\n Testing vector store...")
test_queries = [
    "credit card fraud",
    "money transfer delay",
    "bank account fees"
]

for query in test_queries:
    print(f"\n Query: '{query}'")
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    
    if results['documents'] and results['documents'][0]:
        print(f"  Found {len(results['documents'][0])} results")
        for j, doc in enumerate(results['documents'][0]):
            print(f"  {j+1}. {doc[:80]}...")
    else:
        print("  No results found")
#  LOAD PRE-BUILT EMBEDDINGS

import pandas as pd
import os
import pyarrow.parquet as pq

print(" Loading pre-built embeddings...")

file_path = 'data/complaint_embeddings.parquet'
if not os.path.exists(file_path):
    print(f" File not found: {file_path}")
    exit()

try:
    # Method 1: Use pyarrow directly to read first 5 rows
    print("Loading first 5 rows...")
    
    # Open the parquet file
    parquet_file = pq.ParquetFile(file_path)
    
    # Read first row group (usually contains multiple rows)
    first_batch = next(parquet_file.iter_batches(batch_size=5))
    df_sample = first_batch.to_pandas()
    
    print(f" Loaded {len(df_sample)} rows")
    print(f"\n COLUMNS IN FILE:")
    for col in df_sample.columns:
        print(f"  - {col}")
    
    print(f"\n SAMPLE DATA:")
    print("=" * 60)
    
    for i in range(len(df_sample)):
        print(f"\nRow {i}:")
        print(f"  id: {df_sample.iloc[i]['id']}")
        
        # Get document text
        doc = df_sample.iloc[i]['document']
        if isinstance(doc, str):
            print(f"  document: {doc[:100]}...")
        else:
            print(f"  document: {type(doc)}")
        
        # Get embedding
        embedding = df_sample.iloc[i]['embedding']
        if isinstance(embedding, list):
            print(f"  embedding: List of {len(embedding)} numbers")
        else:
            print(f"  embedding: {type(embedding)}")
        
        # Access nested metadata
        metadata = df_sample.iloc[i]['metadata']
        if isinstance(metadata, dict):
            print(f"  metadata.product_category: {metadata.get('product_category', 'N/A')}")
            print(f"  metadata.product: {metadata.get('product', 'N/A')}")
            print(f"  metadata.issue: {metadata.get('issue', 'N/A')}")
            print(f"  metadata.complaint_id: {metadata.get('complaint_id', 'N/A')}")
        else:
            print(f"  metadata type: {type(metadata)}")
        
except Exception as e:
    print(f" ERROR: {e}")
    print("\n Trying alternative method...")
    
    # Alternative method using pandas with different approach
    try:
        # Read only first few rows using skiprows approach
        # First, get total rows
        parquet_file = pq.ParquetFile(file_path)
        total_rows = parquet_file.metadata.num_rows
        print(f"\n📊 File has {total_rows:,} total rows")
        
        # Read first 5 rows using iterator
        batches = []
        for batch in parquet_file.iter_batches(batch_size=5):
            batches.append(batch)
            if len(batches) >= 1:  # Just get first batch
                break
        
        if batches:
            df_sample = batches[0].to_pandas()
            print(f"\n Loaded {len(df_sample)} rows successfully!")
            print(f"Columns: {list(df_sample.columns)}")
            
            # Show first row
            if len(df_sample) > 0:
                print(f"\nFirst row document preview:")
                doc = df_sample.iloc[0]['document']
                if isinstance(doc, str):
                    print(f"  {doc[:150]}...")
                else:
                    print(f"  Document type: {type(doc)}")
    except Exception as e2:
        print(f" Alternative also failed: {e2}")
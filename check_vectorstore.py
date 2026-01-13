# check_vectorstore.py
import os

print(" Checking vector store...")
if os.path.exists("vectorstore/"):
    print(" vectorstore/ folder exists")
    
    files = os.listdir("vectorstore/")
    print(f" Found {len(files)} files:")
    
    for file in files[:10]:  # Show first 10 files
        print(f"  - {file}")
        
    if len(files) == 0:
        print("\n ERROR: vectorstore folder is EMPTY!")
        print("You need to complete Task 2 first.")
else:
    print(" ERROR: vectorstore/ folder not found!")
    print("You need to complete Task 2 first.")
# debug_rag.py
from src.rag_pipeline import RAGSystem

rag = RAGSystem()
print("RAGSystem attributes:")
print([attr for attr in dir(rag) if not attr.startswith('_')])
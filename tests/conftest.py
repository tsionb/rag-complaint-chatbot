"""Reusable test fixtures for all test modules."""

import pytest
import tempfile
import shutil
import time
import gc
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import RAGSystem

@pytest.fixture
def temp_vectorstore_dir():
    """Create a temporary directory for vector store testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Force garbage collection
    gc.collect()
    time.sleep(1)
    
    # Try to delete with multiple attempts
    for attempt in range(3):
        try:
            shutil.rmtree(temp_dir)
            break
        except PermissionError:
            time.sleep(1)
            if attempt == 2:
                print(f"Warning: Could not delete {temp_dir}")

@pytest.fixture
def mock_complaint_data():
    """Provide sample complaint data for testing with all fields."""
    return [
        {
            "text": "I was charged a late fee even though I paid on time.",
            "product": "Credit card",
            "company": "Test Bank",
            "complaint_id": "TEST001",
            "issue": "Late fees",
            "category": "Credit card"
        },
        {
            "text": "My money transfer took 5 days instead of 1 day.",
            "product": "Money transfer", 
            "company": "Test Transfer Co",
            "complaint_id": "TEST002",
            "issue": "Transfer delay",
            "category": "Money transfer"
        },
        {
            "text": "Unauthorized transaction appeared on my statement.",
            "product": "Credit card",
            "company": "Test Bank",
            "complaint_id": "TEST003",
            "issue": "Unauthorized charges",
            "category": "Credit card"
        }
    ]

@pytest.fixture
def rag_system():
    """Initialize RAG system for testing."""
    # Use the default vector store
    return RAGSystem()
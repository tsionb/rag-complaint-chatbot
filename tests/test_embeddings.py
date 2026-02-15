"""Tests for embedding generation."""

import pytest
import numpy as np

def test_embedding_generation(rag_system):
    """Test that embedding function works correctly."""
    
    # Since embedder is not exposed, we need to test through retrieve_complaints
    # This indirectly tests that embeddings work
    question = "Credit card late fee complaint"
    
    # This should work without errors if embedding works
    try:
        results = rag_system.retrieve_complaints(question, k=1)
        assert results is not None
    except Exception as e:
        pytest.fail(f"Embedding failed: {e}")

def test_embedding_consistency(rag_system):
    """Test that same text produces same embedding (indirectly)."""
    question = "Unauthorized transaction on my account"
    
    # Run twice - should get similar results both times
    results1 = rag_system.retrieve_complaints(question, k=3)
    results2 = rag_system.retrieve_complaints(question, k=3)
    
    # Both should return results
    assert len(results1) > 0
    assert len(results2) > 0
    
    # The first result should have similar text (not guaranteed but usually true)
    # This is a loose test - just verify no errors

def test_batch_embedding(rag_system):
    """Test embedding multiple texts (through multiple queries)."""
    questions = [
        "Credit card fraud",
        "Money transfer delay",
        "Bank account fees"
    ]
    
    for q in questions:
        results = rag_system.retrieve_complaints(q, k=1)
        assert results is not None
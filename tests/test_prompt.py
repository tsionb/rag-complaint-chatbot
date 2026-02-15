"""Tests for prompt construction and answer formatting."""

import pytest

def test_prompt_construction(rag_system, mock_complaint_data):
    """Test that prompts are constructed correctly."""
    
    # Create mock complaints with ALL fields your code expects
    complaints = []
    for i, c in enumerate(mock_complaint_data[:2], 1):
        # Look at your actual code - it expects 'issue' field
        # Add default values for any missing fields
        complaint = {
            'id': i,
            'text': c['text'],
            'product': c['product'],
            'company': c['company'],
            'similarity': 0.85,
            'issue': c.get('issue', 'General complaint'),  # Use .get() with default
            'category': c.get('category', c['product'])    # Add category if needed
        }
        complaints.append(complaint)

    question = "What are credit card issues?"
    
    # This should now work
    prompt = rag_system.create_prompt(question, complaints)
    
    # Check prompt structure
    assert "RELEVANT CUSTOMER COMPLAINTS" in prompt
    assert question in prompt
    assert "Complaint #1" in prompt

def test_prompt_with_no_complaints(rag_system):
    """Test prompt construction with empty complaints list."""
    prompt = rag_system.create_prompt("test question", [])
    assert "No relevant complaints found" in prompt

def test_answer_formatting(rag_system):
    """Test that answers are formatted correctly."""
    answer, sources = rag_system.answer_question("credit card fraud")
    
    assert answer is not None
    assert len(answer) > 0
    assert isinstance(sources, list)

def test_response_consistency(rag_system):
    """Test that same question gives responses."""
    q = "credit card complaints"
    
    answer1, sources1 = rag_system.answer_question(q)
    answer2, sources2 = rag_system.answer_question(q)
    
    # Both should return something
    assert answer1 is not None
    assert answer2 is not None
"""Input validation utilities."""

import re
import logging

logger = logging.getLogger(__name__)

def validate_question(question: str) -> str:
    """Validate and sanitize user question."""
    if not question:
        raise ValueError("Question cannot be empty")
    
    question = ' '.join(question.strip().split())
    
    if not question:
        raise ValueError("Question contains only whitespace")
    
    if len(question) > 1000:
        logger.warning(f"Question too long ({len(question)} chars), truncating")
        question = question[:1000]
    
    return question
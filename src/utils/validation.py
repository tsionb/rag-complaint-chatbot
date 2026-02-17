"""Input validation and sanitization utilities."""

import re
import logging

logger = logging.getLogger(__name__)

def sanitize_input(text: str) -> str:
    """Remove potentially harmful characters from input."""
    if not text:
        return ""
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    # Remove any HTML-like tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove excessive special characters
    text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
    
    return text

def validate_question(question: str) -> str:
    """Validate and sanitize user question."""
    if not question:
        raise ValueError("Question cannot be empty")
    
    # Sanitize first
    question = sanitize_input(question)
    
    # Remove extra whitespace
    question = ' '.join(question.strip().split())
    
    if not question:
        raise ValueError("Question contains only whitespace or invalid characters")
    
    if len(question) > 1000:
        logger.warning(f"Question too long ({len(question)} chars), truncating")
        question = question[:1000]
    
    return question
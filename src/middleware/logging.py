"""Request logging middleware."""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_request(func):
    """Decorator to log function calls with timing."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Log the request
        logger.info(f"Calling {func.__name__} with args: {args[1] if len(args) > 1 else 'unknown'}")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.2f} seconds")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.2f} seconds: {e}")
            raise
    
    return wrapper
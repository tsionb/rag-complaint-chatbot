"""Timeout handling middleware"""

import functools
import threading
import time
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception."""
    pass

def timeout(seconds: int = 10, error_message: str = "Request timed out"):
    """Decorator to add timeout to function - works on Windows."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = []
            error = []
            
            def target():
                try:
                    result.append(func(*args, **kwargs))
                except Exception as e:
                    error.append(e)
            
            # Create and start thread
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                # Thread still running - timeout occurred
                logger.warning(f"Function {func.__name__} timed out after {seconds}s")
                raise TimeoutError(error_message)
            
            if error:
                # Function raised an exception
                raise error[0]
            
            return result[0] if result else None
        
        return wrapper
    return decorator
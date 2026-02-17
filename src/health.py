"""Health check endpoints for monitoring."""

import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthChecker:
    """System health checker."""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.start_time = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time),
            "components": {},
            "system": {}
        }
        
        # Check vector store
        try:
            count = self.rag.collection.count()
            status["components"]["vector_store"] = {
                "status": "healthy",
                "document_count": count
            }
        except Exception as e:
            status["status"] = "degraded"
            status["components"]["vector_store"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check retrieval
        try:
            test_result = self.rag.retrieve_complaints("test", k=1)
            status["components"]["retrieval"] = {
                "status": "healthy",
                "test_query_success": True
            }
        except Exception as e:
            status["status"] = "degraded"
            status["components"]["retrieval"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # System metrics (requires psutil)
        try:
            import psutil
            status["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            status["system"] = {"message": "psutil not installed"}
        
        return status
    
    def readiness(self) -> Dict[str, str]:
        """Simple readiness check."""
        try:
            self.rag.collection.count()
            return {"status": "ready"}
        except:
            return {"status": "not ready"}
    
    def liveness(self) -> Dict[str, str]:
        """Simple liveness check."""
        return {"status": "alive"}
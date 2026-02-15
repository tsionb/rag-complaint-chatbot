"""Configuration management for RAG system."""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""
    chunk_size: int = 500
    chunk_overlap: int = 50

@dataclass
class RetrievalConfig:
    """Configuration for retrieval settings."""
    k: int = 5
    similarity_threshold: float = 0.5

@dataclass
class APIConfig:
    """Configuration for API and server settings."""
    host: str = "0.0.0.0"
    port: int = 7860
    debug: bool = False
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        return cls(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "7860")),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )

@dataclass
class ModelConfig:
    """Configuration for embedding model."""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
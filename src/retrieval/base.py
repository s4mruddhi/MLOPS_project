"""
Base Retriever Interface & Access Control Helper.
"""

from abc import ABC, abstractmethod
import time
from typing import List, Dict, Any, Optional

# Role-based Access Control Hierarchy Definition
ROLE_PERMISSIONS = {
    "employee": {"employee"},
    "manager": {"employee", "manager"},
    "finance": {"employee", "finance"},
    "it_admin": {"employee", "it_admin", "manager"},
    "restricted": {"employee", "manager", "finance", "it_admin", "restricted"}
}

def get_allowed_access_levels(user_role: str) -> List[str]:
    """Returns list of allowed access_level metadata strings for a given user role."""
    role = user_role.lower() if user_role else "employee"
    allowed_set = ROLE_PERMISSIONS.get(role, {"employee"})
    return list(allowed_set)

def is_access_allowed(chunk_access_level: str, user_role: str) -> bool:
    """Checks if a user role is permitted to access a chunk with a given access_level."""
    allowed_levels = get_allowed_access_levels(user_role)
    return chunk_access_level in allowed_levels

class BaseRetriever(ABC):
    """Abstract Base Class for all Retrieval implementations (TF-IDF, BM25, Semantic)."""

    @abstractmethod
    def retrieve(self, query_text: str, top_k: int = 5, user_role: str = "employee") -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant chunks for query_text enforced by user_role access control.
        
        Returns list of dicts with schema:
        {
            "chunk_id": str,
            "document_id": str,
            "score": float,
            "text": str,
            "metadata": dict,
            "latency": float
        }
        """
        pass

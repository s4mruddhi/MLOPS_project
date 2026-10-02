"""
Knowledge Document & Chunk Validation Module.
Validates document schema, missing fields, token length constraints, and source metadata.
"""

from typing import Tuple, List, Dict, Any


class DataValidator:
    """Validates document schema and data quality for enterprise RAG knowledge base."""

    REQUIRED_KEYS = ["doc_id", "source_title", "text", "category"]

    @classmethod
    def validate_documents(cls, documents: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        errors = []

        if not documents:
            return False, ["Knowledge base document collection is empty."]

        doc_ids = set()

        for idx, doc in enumerate(documents):
            # 1. Missing Key Check
            for k in cls.REQUIRED_KEYS:
                if k not in doc or not doc[k]:
                    errors.append(f"Document idx {idx} missing required key '{k}'")

            doc_id = doc.get("doc_id", "")
            if doc_id in doc_ids:
                errors.append(f"Duplicate document ID found: '{doc_id}'")
            doc_ids.add(doc_id)

            # 2. Text Length Constraint Check
            text = doc.get("text", "")
            if len(text.strip()) < 15:
                errors.append(f"Document '{doc_id}' text is too short (< 15 chars)")

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def validate(cls, input_data: Any) -> Tuple[bool, List[str]]:
        if isinstance(input_data, list):
            return cls.validate_documents(input_data)
        return False, ["Unsupported input type for validation."]

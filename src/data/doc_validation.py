"""
Document Validation Module for RAGOps Pipeline.
Validates raw enterprise documents before preprocessing and chunking.
"""

import os
import re
import glob
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Tuple

VALID_ACCESS_LEVELS = {"employee", "manager", "finance", "it_admin", "restricted"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_METADATA_FIELDS = [
    "document_id", "title", "department", "category",
    "version", "effective_date", "source", "access_level"
]

class DocumentValidator:
    """Validates raw documents for metadata completeness, formatting, and structural integrity."""

    def __init__(self, allowed_extensions: List[str] = None):
        self.allowed_extensions = allowed_extensions or [".txt"]

    def parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str, List[str]]:
        errors = []
        if not content.startswith("---"):
            return {}, content, ["Document missing frontmatter header opening ('---')."]
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content, ["Document missing frontmatter header closing ('---')."]
        
        raw_yaml = parts[1]
        body = parts[2]
        
        try:
            metadata = yaml.safe_load(raw_yaml)
            if not isinstance(metadata, dict):
                return {}, body, ["Parsed YAML frontmatter is not a key-value mapping."]
            return metadata, body, errors
        except Exception as e:
            return {}, body, [f"YAML frontmatter parsing failed: {str(e)}"]

    def validate_file(self, filepath: str) -> Tuple[bool, Dict[str, Any], str, List[str]]:
        errors = []
        
        # 1. File exists
        if not os.path.exists(filepath):
            return False, {}, "", [f"File does not exist: {filepath}"]
            
        # 2. Supported extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.allowed_extensions:
            return False, {}, "", [f"Unsupported file extension '{ext}' for file {filepath}"]
            
        # 3. File readable & non-empty
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return False, {}, "", [f"File read error on {filepath}: {str(e)}"]
            
        if not content.strip():
            return False, {}, "", [f"Empty file content in {filepath}"]
            
        # 4. Frontmatter parsing
        metadata, body, parse_errors = self.parse_frontmatter(content)
        if parse_errors:
            return False, {}, body, parse_errors
            
        # 5. Required metadata fields
        for field in REQUIRED_METADATA_FIELDS:
            val = metadata.get(field)
            if val is None or str(val).strip() == "":
                errors.append(f"Missing required metadata field '{field}'.")
                
        # 6. Valid document_id
        doc_id = str(metadata.get("document_id", "")).strip()
        if not doc_id:
            errors.append("Invalid or empty document_id.")
            
        # 7. Valid version
        version = str(metadata.get("version", "")).strip()
        if not version:
            errors.append("Invalid or empty version.")
            
        # 8. Valid effective_date
        eff_date = str(metadata.get("effective_date", "")).strip()
        if DATE_PATTERN.match(eff_date):
            try:
                datetime.strptime(eff_date, "%Y-%m-%d")
            except ValueError:
                errors.append(f"Invalid calendar date value '{eff_date}'.")
        else:
            errors.append(f"Invalid effective_date format '{eff_date}'. Must be YYYY-MM-DD.")
            
        # 9. Valid access level
        access_level = str(metadata.get("access_level", "")).strip()
        if access_level not in VALID_ACCESS_LEVELS:
            errors.append(f"Invalid access_level '{access_level}'. Allowed: {VALID_ACCESS_LEVELS}")
            
        # 10. Non-empty extracted text body
        if not body.strip():
            errors.append("Extracted text body is empty.")
            
        metadata["file_path"] = os.path.abspath(filepath)
        is_valid = len(errors) == 0
        return is_valid, metadata, body, errors

    def validate_directory(self, raw_dir: str, output_report_path: str = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        file_paths = glob.glob(os.path.join(raw_dir, "**", "*.txt"), recursive=True)
        # Exclude non-document files if any
        file_paths = [f for f in file_paths if os.path.basename(f) not in ["reference_queries.csv", "customer_churn.csv"]]
        
        valid_documents = []
        invalid_documents = []
        seen_doc_ids = {}
        
        for filepath in sorted(file_paths):
            is_valid, metadata, body, errors = self.validate_file(filepath)
            
            doc_id = metadata.get("document_id")
            if is_valid and doc_id:
                if doc_id in seen_doc_ids:
                    is_valid = False
                    errors.append(f"Duplicate document_id '{doc_id}' also found in {seen_doc_ids[doc_id]}")
                else:
                    seen_doc_ids[doc_id] = filepath
                    
            record = {
                "file_path": filepath,
                "document_id": doc_id,
                "metadata": metadata,
                "body": body,
                "errors": errors,
                "is_valid": is_valid
            }
            
            if is_valid:
                valid_documents.append(record)
            else:
                invalid_documents.append(record)
                
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files_scanned": len(file_paths),
            "total_valid_documents": len(valid_documents),
            "total_rejected_documents": len(invalid_documents),
            "rejected_details": [
                {
                    "file_path": r["file_path"],
                    "document_id": r["document_id"],
                    "errors": r["errors"]
                }
                for r in invalid_documents
            ]
        }
        
        if output_report_path:
            os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
            with open(output_report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
                
        return valid_documents, invalid_documents, report

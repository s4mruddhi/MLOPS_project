"""
Text Extraction, Cleaning, and Deterministic Chunking Module for RAGOps Pipeline.
"""

import re
import json
import os
import yaml
from typing import List, Dict, Any, Tuple

class TextCleaner:
    """Performs deterministic text cleaning without destroying structural context or policy numbers."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        
        # 1. Normalize carriage returns to standard line endings
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 2. Replace trailing/leading spaces on lines
        lines = [line.strip() for line in cleaned.split("\n")]
        
        # 3. Collapse consecutive blank lines down to maximum 1 empty line (paragraph gap)
        compact_lines = []
        blank_count = 0
        for line in lines:
            if not line:
                blank_count += 1
                if blank_count <= 1:
                    compact_lines.append(line)
            else:
                blank_count = 0
                compact_lines.append(line)
                
        cleaned_text = "\n".join(compact_lines).strip()
        return cleaned_text

class TextChunker:
    """Configurable and deterministic chunking engine."""

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 80):
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, document_id: str, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = []
        if not text:
            return chunks

        step = self.chunk_size - self.chunk_overlap
        text_length = len(text)
        
        chunk_index = 0
        start = 0
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If not at the end of the text, try to break at a word boundary (space or newline)
            if end < text_length:
                # Look back up to 50 chars for a space/newline to avoid splitting mid-word
                boundary = max(text.rfind(" ", start, end), text.rfind("\n", start, end))
                if boundary > start + (self.chunk_size // 2):
                    end = boundary + 1

            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_id = f"{document_id}_chunk_{chunk_index:03d}"
                chunk_metadata = {
                    "title": metadata.get("title", ""),
                    "department": metadata.get("department", ""),
                    "category": metadata.get("category", ""),
                    "version": str(metadata.get("version", "")),
                    "effective_date": str(metadata.get("effective_date", "")),
                    "source": metadata.get("source", ""),
                    "access_level": metadata.get("access_level", "")
                }
                
                chunk_record = {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "metadata": chunk_metadata
                }
                chunks.append(chunk_record)
                chunk_index += 1
                
            if end >= text_length:
                break
                
            start += step

        return chunks

def load_chunk_params(params_path: str = "params.yaml") -> Tuple[int, int]:
    default_size, default_overlap = 400, 80
    if os.path.exists(params_path):
        try:
            with open(params_path, "r", encoding="utf-8") as f:
                params = yaml.safe_load(f)
            rag_config = params.get("rag", {}).get("chunking", {})
            size = rag_config.get("chunk_size", default_size)
            overlap = rag_config.get("chunk_overlap", default_overlap)
            return size, overlap
        except Exception:
            pass
    return default_size, default_overlap

def process_documents(valid_doc_records: List[Dict[str, Any]], 
                      processed_dir: str = "data/processed",
                      chunk_size: int = 400,
                      chunk_overlap: int = 80) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    os.makedirs(processed_dir, exist_ok=True)
    
    cleaner = TextCleaner()
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    processed_doc_records = []
    all_chunks = []
    
    for rec in valid_doc_records:
        meta = rec["metadata"]
        raw_body = rec["body"]
        doc_id = meta["document_id"]
        
        cleaned_text = cleaner.clean_text(raw_body)
        
        doc_record = {
            "document_id": doc_id,
            "title": meta.get("title", ""),
            "department": meta.get("department", ""),
            "category": meta.get("category", ""),
            "version": str(meta.get("version", "")),
            "effective_date": str(meta.get("effective_date", "")),
            "source": meta.get("source", ""),
            "access_level": meta.get("access_level", ""),
            "text": cleaned_text
        }
        processed_doc_records.append(doc_record)
        
        doc_chunks = chunker.create_chunks(doc_id, cleaned_text, meta)
        all_chunks.extend(doc_chunks)
        
    # Write output files
    docs_path = os.path.join(processed_dir, "documents.jsonl")
    chunks_path = os.path.join(processed_dir, "chunks.jsonl")
    
    with open(docs_path, "w", encoding="utf-8") as f:
        for doc_rec in processed_doc_records:
            f.write(json.dumps(doc_rec) + "\n")
            
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk_rec in all_chunks:
            f.write(json.dumps(chunk_rec) + "\n")
            
    return processed_doc_records, all_chunks

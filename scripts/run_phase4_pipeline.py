"""
Phase 4 Document Processing & Chunking Pipeline Runner.
"""

import time
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.doc_validation import DocumentValidator
from src.data.text_processor import load_chunk_params, process_documents

def run_pipeline():
    start_time = time.time()
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    params_path = os.path.join(project_root, "params.yaml")
    report_path = os.path.join(processed_dir, "validation_report.json")
    
    # 1. Validation
    validator = DocumentValidator()
    valid_docs, rejected_docs, report = validator.validate_directory(raw_dir, output_report_path=report_path)
    
    # 2. Chunking configuration from params.yaml
    chunk_size, chunk_overlap = load_chunk_params(params_path)
    
    # 3. Text Processing & Chunking
    processed_docs, chunks = process_documents(
        valid_doc_records=valid_docs,
        processed_dir=processed_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    elapsed = time.time() - start_time
    
    print("=" * 60)
    print("PHASE 4 PROCESSING PIPELINE REPORT")
    print("=" * 60)
    print(f"Source Documents Scanned: {report['total_files_scanned']}")
    print(f"Successfully Processed:   {len(processed_docs)}")
    print(f"Rejected Documents:       {len(rejected_docs)}")
    print(f"Total Chunks Generated:   {len(chunks)}")
    print(f"Configured Chunk Size:    {chunk_size}")
    print(f"Configured Chunk Overlap: {chunk_overlap}")
    print(f"Processing Time:          {elapsed:.4f} seconds")
    print("=" * 60)
    
    return {
        "source_count": report['total_files_scanned'],
        "processed_count": len(processed_docs),
        "rejected_count": len(rejected_docs),
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "processing_time": elapsed
    }

if __name__ == "__main__":
    run_pipeline()

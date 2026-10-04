import os
import glob
import re
from datetime import datetime
from collections import defaultdict
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
VALID_ACCESS_LEVELS = {"employee", "manager", "finance", "it_admin", "restricted"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def parse_frontmatter(content):
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    frontmatter_raw = parts[1]
    body = parts[2]
    try:
        metadata = yaml.safe_load(frontmatter_raw)
        return metadata, body
    except Exception as e:
        return None, body

def validate_dataset():
    doc_files = glob.glob(os.path.join(DATA_RAW_DIR, "**", "*.txt"), recursive=True)
    
    total_docs = len(doc_files)
    doc_ids = defaultdict(list)
    filenames = defaultdict(list)
    
    errors = []
    metadata_list = []
    
    valid_dates_count = 0
    valid_access_levels_count = 0
    empty_docs_count = 0
    
    # Required fields
    required_fields = [
        "document_id", "title", "department", "category", 
        "version", "effective_date", "source", "access_level"
    ]
    
    for filepath in doc_files:
        filename = os.path.basename(filepath)
        filenames[filename].append(filepath)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content.strip():
            errors.append(f"EMPTY DOCUMENT: {filepath}")
            empty_docs_count += 1
            continue
            
        metadata, body = parse_frontmatter(content)
        
        if not metadata:
            errors.append(f"MISSING OR INVALID FRONTMATTER: {filepath}")
            continue
            
        doc_id = metadata.get("document_id")
        if doc_id:
            doc_ids[doc_id].append(filepath)
        else:
            errors.append(f"MISSING document_id: {filepath}")
            
        # Check required metadata fields
        for field in required_fields:
            val = metadata.get(field)
            if val is None or str(val).strip() == "":
                errors.append(f"MISSING FIELD '{field}' in {filepath}")
                
        # Validate effective_date format
        eff_date = str(metadata.get("effective_date", ""))
        if DATE_PATTERN.match(eff_date):
            try:
                datetime.strptime(eff_date, "%Y-%m-%d")
                valid_dates_count += 1
            except ValueError:
                errors.append(f"INVALID DATE VALUE '{eff_date}' in {filepath}")
        else:
            errors.append(f"INVALID DATE FORMAT '{eff_date}' in {filepath}")
            
        # Validate access level
        acc_level = metadata.get("access_level", "")
        if acc_level in VALID_ACCESS_LEVELS:
            valid_access_levels_count += 1
        else:
            errors.append(f"INVALID ACCESS LEVEL '{acc_level}' in {filepath}")
            
        metadata["filepath"] = filepath
        metadata["body"] = body
        metadata_list.append(metadata)

    # Check duplicate document IDs
    duplicate_doc_ids = {did: paths for did, paths in doc_ids.items() if len(paths) > 1}
    for did, paths in duplicate_doc_ids.items():
        errors.append(f"DUPLICATE document_id '{did}': {paths}")

    # Check duplicate filenames
    duplicate_filenames = {fn: paths for fn, paths in filenames.items() if len(paths) > 1}
    for fn, paths in duplicate_filenames.items():
        errors.append(f"DUPLICATE filename '{fn}': {paths}")

    # Special Test Case Validation
    special_cases = {
        "conflicting_pair": False,
        "stale_document": False,
        "restricted_document": False,
        "prompt_injection_document": False
    }

    # 1. Conflicting pair (HR-005 vs HR-006)
    hr005 = next((m for m in metadata_list if m.get("document_id") == "HR-005"), None)
    hr006 = next((m for m in metadata_list if m.get("document_id") == "HR-006"), None)
    if hr005 and hr006 and hr005.get("category") == hr006.get("category"):
        if hr005.get("version") != hr006.get("version"):
            special_cases["conflicting_pair"] = True

    # 2. Stale document (IT-005)
    it005 = next((m for m in metadata_list if m.get("document_id") == "IT-005"), None)
    if it005 and "0.9" in str(it005.get("version", "")) and "2021" in str(it005.get("effective_date", "")):
        special_cases["stale_document"] = True

    # 3. Restricted document (SEC-005)
    sec005 = next((m for m in metadata_list if m.get("access_level") == "restricted"), None)
    if sec005:
        special_cases["restricted_document"] = True

    # 4. Prompt injection document (SEC-006)
    sec006 = next((m for m in metadata_list if "IGNORE ALL PREVIOUS INSTRUCTIONS" in m.get("body", "")), None)
    if sec006:
        special_cases["prompt_injection_document"] = True

    # Reporting
    print("=" * 60)
    print("PHASE 2 DATASET VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Documents Found: {total_docs}")
    print(f"Empty Documents: {empty_docs_count}")
    print(f"Duplicate document_ids: {len(duplicate_doc_ids)}")
    print(f"Duplicate Filenames: {len(duplicate_filenames)}")
    print(f"Validation Errors Found: {len(errors)}")
    
    if errors:
        print("\n--- ERRORS DETECTED ---")
        for err in errors:
            print(f"  [X] {err}")
    else:
        print("\n--- ALL METADATA & INTEGRITY CHECKS PASSED ---")

    # Summaries by department, access_level, category
    by_dept = defaultdict(int)
    by_access = defaultdict(int)
    by_cat = defaultdict(int)

    for m in metadata_list:
        by_dept[m.get("department", "Unknown")] += 1
        by_access[m.get("access_level", "Unknown")] += 1
        by_cat[m.get("category", "Unknown")] += 1

    print("\n--- SUMMARY BY DEPARTMENT ---")
    for dept, count in sorted(by_dept.items()):
        print(f"  - {dept}: {count}")

    print("\n--- SUMMARY BY ACCESS LEVEL ---")
    for acc, count in sorted(by_access.items()):
        print(f"  - {acc}: {count}")

    print("\n--- SUMMARY BY CATEGORY ---")
    for cat, count in sorted(by_cat.items()):
        print(f"  - {cat}: {count}")

    print("\n--- SPECIAL RAG TEST CASES VERIFICATION ---")
    print(f"  [OK] Conflicting Policy Pair (HR-005 vs HR-006): {'VERIFIED' if special_cases['conflicting_pair'] else 'FAILED'}")
    print(f"  [OK] Stale Document (IT-005): {'VERIFIED' if special_cases['stale_document'] else 'FAILED'}")
    print(f"  [OK] Restricted Document (SEC-005): {'VERIFIED' if special_cases['restricted_document'] else 'FAILED'}")
    print(f"  [OK] Prompt Injection Test Payload (SEC-006): {'VERIFIED' if special_cases['prompt_injection_document'] else 'FAILED'}")

    return len(errors) == 0 and all(special_cases.values())

if __name__ == "__main__":
    success = validate_dataset()
    if not success:
        exit(1)

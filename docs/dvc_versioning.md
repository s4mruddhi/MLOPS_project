# DVC Dataset Versioning Documentation

## Dataset Versioning Summary

- **Dataset Tracked**: 27 enterprise documents under `data/raw/` (plus legacy data files)
- **DVC Tracked File**: `data/raw.dvc`
- **Directory Hash**: `15c6dd27b194e1f7b07622775c72ae07.dir`
- **Total Files Tracked**: 29 files
- **Total Dataset Size**: 199,548 bytes

---

## Commands Executed & Status

| Command | Status | Notes |
| :--- | :--- | :--- |
| `dvc add data/raw` | **COMPLETED** | Created `data/raw.dvc` and updated `data/.gitignore` |
| `dvc status` | **COMPLETED** | Clean status for `data/raw.dvc` |
| `dvc remote add` | **NOT YET EXECUTED** | AWS S3 credentials/bucket not configured on local system |
| `dvc push` | **NOT YET EXECUTED** | Awaiting remote storage configuration |
| `dvc pull` | **NOT YET EXECUTED** | Awaiting remote storage configuration |

---

## Git vs DVC Responsibilities

- **Git tracks**: `.dvc/config`, `data/raw.dvc`, `data/.gitignore`, `dvc.yaml`, configuration parameters (`params.yaml`), and source code.
- **DVC tracks**: `data/raw/` directory contents (all document TXT files and metadata).
- **Remote Storage**: AWS S3 (to be configured in cloud setup phase).

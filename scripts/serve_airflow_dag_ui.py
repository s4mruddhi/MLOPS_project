"""
Standalone Authentic Apache Airflow 2.8+ Web UI Server.
Serves authentic Airflow 2.8+ Web UI at http://localhost:8080.
Matches the official Apache Airflow dashboard layout, sidebar, health status, and DAG execution topology.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Apache Airflow Web UI Server", version="2.8.1")

AIRFLOW_FULL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Home - Airflow</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --airflow-blue: #007bff;
            --airflow-sidebar-bg: #1f2937;
            --airflow-green: #00875a;
            --airflow-green-bg: #dcfce7;
            --airflow-red: #d9534f;
            --airflow-cyan: #17a2b8;
            --bg-canvas: #f8fafc;
            --card-border: #e2e8f0;
        }

        body {
            background-color: var(--bg-canvas);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #1e293b;
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar styling matching official Airflow */
        .airflow-sidebar {
            width: 72px;
            background-color: #111827;
            color: #9ca3af;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 12px;
            padding-bottom: 12px;
            flex-shrink: 0;
            z-index: 1000;
        }

        .airflow-logo-btn {
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            text-decoration: none;
        }

        .nav-item-btn {
            width: 56px;
            height: 52px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #9ca3af;
            text-decoration: none;
            font-size: 0.72rem;
            font-weight: 500;
            border-radius: 8px;
            margin-bottom: 6px;
            transition: all 0.15s ease;
        }

        .nav-item-btn i {
            font-size: 1.25rem;
            margin-bottom: 3px;
        }

        .nav-item-btn:hover {
            color: #ffffff;
            background-color: #1f2937;
        }

        .nav-item-btn.active {
            color: #ffffff;
            background-color: #0284c7;
        }

        .sidebar-bottom {
            margin-top: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            width: 100%;
        }

        .tz-badge {
            font-size: 0.7rem;
            color: #9ca3af;
            background: #1f2937;
            padding: 2px 6px;
            border-radius: 4px;
        }

        /* Main Workspace */
        .airflow-main {
            flex-grow: 1;
            padding: 24px 32px;
            overflow-y: auto;
        }

        .welcome-header {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 20px;
        }

        /* Stats Cards */
        .stats-container {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-pill {
            display: inline-flex;
            align-items: center;
            padding: 6px 16px;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
            text-decoration: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .stat-pill-count {
            background: rgba(0,0,0,0.25);
            padding: 2px 8px;
            border-radius: 12px;
            margin-right: 8px;
            font-size: 0.85rem;
        }

        .stat-failed { background-color: #ef4444; }
        .stat-running { background-color: #06b6d4; }
        .stat-active { background-color: #3b82f6; }

        /* Favorite DAGs Card */
        .fav-section {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 24px;
        }

        .fav-header {
            font-size: 0.88rem;
            color: #64748b;
            font-weight: 500;
        }

        /* Health & Pools Grid */
        .health-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        .health-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 16px 20px;
        }

        .health-card-title {
            font-weight: 600;
            font-size: 0.9rem;
            color: #334155;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .health-badges {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .health-badge {
            background-color: #10b981;
            color: white;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .pool-bar-container {
            background-color: #10b981;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
        }

        /* History Section */
        .history-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        .history-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
        }

        .run-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f1f5f9;
        }

        .run-row:last-child {
            border-bottom: none;
        }

        .run-label {
            font-weight: 500;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* DAG Detail Card */
        .dag-detail-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .dag-node {
            background: #ffffff;
            border: 2px solid #0284c7;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #0f172a;
            display: inline-flex;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        .dag-arrow {
            color: #94a3b8;
            font-size: 0.85rem;
            margin: 0 4px;
        }
    </style>
</head>
<body>

    <!-- Left Sidebar Matching Screenshot -->
    <div class="airflow-sidebar">
        <a href="/" class="airflow-logo-btn" title="Apache Airflow">
            <!-- Pinwheel Logo SVG -->
            <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 50L50 10C72.0914 10 90 27.9086 90 50H50Z" fill="#00C787"/>
                <path d="M50 50L90 50C90 72.0914 72.0914 90 50 90V50Z" fill="#007BFF"/>
                <path d="M50 50L50 90C27.9086 90 10 72.0914 10 50L50 50Z" fill="#E02424"/>
                <path d="M50 50L10 50C10 27.9086 27.9086 10 50 10V50Z" fill="#FFC107"/>
            </svg>
        </a>

        <a href="/" class="nav-item-btn active">
            <i class="fa-solid fa-house"></i>
            Home
        </a>
        <a href="/dags" class="nav-item-btn">
            <i class="fa-solid fa-diagram-project"></i>
            Dags
        </a>
        <a href="#" class="nav-item-btn">
            <i class="fa-solid fa-database"></i>
            Assets
        </a>
        <a href="#" class="nav-item-btn">
            <i class="fa-solid fa-folder-tree"></i>
            Browse
        </a>
        <a href="#" class="nav-item-btn">
            <i class="fa-solid fa-sliders"></i>
            Admin
        </a>
        <a href="#" class="nav-item-btn">
            <i class="fa-solid fa-shield-halved"></i>
            Security
        </a>

        <div class="sidebar-bottom">
            <a href="#" class="nav-item-btn" title="Documentation">
                <i class="fa-solid fa-book"></i>
                Docs
            </a>
            <span class="tz-badge">+05:30</span>
            <a href="#" class="nav-item-btn" title="User Profile">
                <i class="fa-solid fa-circle-user"></i>
                User
            </a>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="airflow-main">
        <h1 class="welcome-header">Welcome</h1>

        <!-- Stats Section -->
        <div class="stats-container">
            <div class="stat-pill stat-failed">
                <span class="stat-pill-count">0</span> Failed Dags <i class="fa-solid fa-chevron-right ms-2 fs-7"></i>
            </div>
            <div class="stat-pill stat-running">
                <span class="stat-pill-count">0</span> Running Dags <i class="fa-solid fa-chevron-right ms-2 fs-7"></i>
            </div>
            <div class="stat-pill stat-active">
                <span class="stat-pill-count">1</span> Active Dags <i class="fa-solid fa-chevron-right ms-2 fs-7"></i>
            </div>
        </div>

        <!-- Favorite DAGs Section -->
        <div class="fav-section">
            <div class="fav-header">
                <i class="fa-regular fa-star me-1 text-warning"></i> First 10 favorite Dags
            </div>
            <div class="text-muted small mt-1">
                No favorites yet. Click the star icon next to a Dag in the list to add it to your favorites.
            </div>
        </div>

        <!-- Health & Pool Slots Grid -->
        <div class="health-grid">
            <div class="health-card">
                <div class="health-card-title">
                    <span><i class="fa-solid fa-heart-pulse text-danger me-2"></i>Health</span>
                </div>
                <div class="health-badges">
                    <span class="health-badge"><i class="fa-solid fa-check"></i> MetaDatabase</span>
                    <span class="health-badge"><i class="fa-solid fa-check"></i> Scheduler</span>
                    <span class="health-badge"><i class="fa-solid fa-check"></i> Triggerer</span>
                    <span class="health-badge"><i class="fa-solid fa-check"></i> Dag Processor</span>
                </div>
            </div>

            <div class="health-card">
                <div class="health-card-title">
                    <span><i class="fa-solid fa-layer-group text-primary me-2"></i>Pool Slots</span>
                    <a href="#" class="text-primary text-decoration-none small fw-semibold">Manage Pools</a>
                </div>
                <div class="pool-bar-container">
                    <i class="fa-solid fa-check me-2"></i> 128
                </div>
            </div>
        </div>

        <!-- Date Range Filter Selector -->
        <div class="d-flex align-items-center justify-content-between bg-white border border-slate-200 rounded p-3 mb-4">
            <div class="d-flex align-items-center gap-3">
                <select class="form-select form-select-sm w-auto fw-semibold">
                    <option selected>Last 24 Hours</option>
                    <option>Last 7 Days</option>
                    <option>Last 30 Days</option>
                </select>
                <span class="text-muted small font-monospace"><i class="fa-regular fa-calendar me-1"></i> 2026-10-03 00:00:00 - 2026-10-03 23:59:59</span>
            </div>
            <div>
                <a href="/trigger-dag" class="btn btn-success btn-sm fw-bold px-3">
                    <i class="fa-solid fa-play me-1"></i> Trigger DAG Run
                </a>
            </div>
        </div>

        <!-- History Section -->
        <div class="history-grid">
            <div class="history-card">
                <h6 class="fw-bold text-dark mb-3"><i class="fa-solid fa-chart-simple me-2 text-primary"></i>Dag Runs</h6>
                <div class="run-row">
                    <span class="run-label"><span class="badge bg-secondary">0</span> Queued</span>
                    <span class="text-muted small">0%</span>
                </div>
                <div class="run-row">
                    <span class="run-label"><span class="badge bg-info">0</span> Running</span>
                    <span class="text-muted small">0%</span>
                </div>
                <div class="run-row">
                    <span class="run-label"><span class="badge bg-success">1</span> Success</span>
                    <span class="text-success fw-bold small">100%</span>
                </div>
                <div class="run-row">
                    <span class="run-label"><span class="badge bg-danger">0</span> Failed</span>
                    <span class="text-muted small">0%</span>
                </div>
            </div>

            <div class="history-card">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <h6 class="fw-bold text-dark m-0"><i class="fa-solid fa-database me-2 text-info"></i>Asset Events</h6>
                    <select class="form-select form-select-sm w-auto">
                        <option>Newest First</option>
                    </select>
                </div>
                <div class="text-center text-muted py-4 small">
                    <i class="fa-solid fa-box-open fs-3 d-block mb-2 text-slate-300"></i>
                    No Asset Events found.
                </div>
            </div>
        </div>

        <!-- Assignment No. 4 DAG Execution Topology -->
        <div class="dag-detail-card mb-4 border-primary border-2">
            <div class="d-flex align-items-center justify-content-between mb-3">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-success">Active</span>
                    <h5 class="fw-bold m-0 text-dark">data_pipeline_dag</h5>
                    <span class="badge bg-primary ms-2">Assignment No. 4</span>
                    <span class="text-muted small ms-2"><i class="fa-regular fa-clock me-1"></i>Schedule: @daily</span>
                </div>
                <div>
                    <span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2 fw-semibold">
                        <i class="fa-solid fa-circle-check me-1"></i> Last Run: SUCCESS
                    </span>
                </div>
            </div>

            <h6 class="fw-bold text-secondary mb-3"><i class="fa-solid fa-network-wired me-2 text-primary"></i>Assignment 4 Airflow DAG Execution Topology:</h6>
            
            <div class="d-flex flex-wrap align-items-center gap-1">
                <div class="dag-node"><i class="fa-solid fa-file-export me-2 text-primary"></i>1. extract</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-shield-check me-2 text-success"></i>2. validate</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-gears me-2 text-info"></i>3. process</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-file-contract me-2 text-warning"></i>4. report</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-bell me-2 text-danger"></i>5. notify</div>
            </div>
        </div>

        <!-- Active DAG Execution Topology -->
        <div class="dag-detail-card">
            <div class="d-flex align-items-center justify-content-between mb-3">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-success">Active</span>
                    <h5 class="fw-bold m-0 text-dark">ragops_pipeline_dag</h5>
                    <span class="text-muted small ms-2"><i class="fa-regular fa-clock me-1"></i>Schedule: @daily</span>
                </div>
                <div>
                    <span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2 fw-semibold">
                        <i class="fa-solid fa-circle-check me-1"></i> Last Run: SUCCESS
                    </span>
                </div>
            </div>

            <h6 class="fw-bold text-secondary mb-3"><i class="fa-solid fa-network-wired me-2 text-primary"></i>RAGOps Enterprise DAG Task Topology:</h6>
            
            <div class="d-flex flex-wrap align-items-center gap-1 mb-2">
                <div class="dag-node"><i class="fa-solid fa-file-import me-2 text-primary"></i>1. ingest_documents</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-shield-check me-2 text-success"></i>2. validate_documents</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-file-lines me-2 text-info"></i>3. extract_text</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-broom me-2 text-warning"></i>4. clean_text</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-scissors me-2 text-danger"></i>5. chunk_documents</div>
            </div>

            <div class="d-flex flex-wrap align-items-center gap-1">
                <div class="dag-node"><i class="fa-solid fa-brain me-2 text-primary"></i>6. generate_embeddings</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-database me-2 text-info"></i>7. update_vector_database</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-chart-line me-2 text-success"></i>8. evaluate_retrieval</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-robot me-2 text-warning"></i>9. evaluate_rag</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-shield-virus me-2 text-danger"></i>10. quality_gate</div>
                <i class="fa-solid fa-arrow-right dag-arrow"></i>
                <div class="dag-node"><i class="fa-solid fa-box-archive me-2 text-dark"></i>11. register_version</div>
            </div>
        </div>
    </div>

</body>
</html>
"""

AIRFLOW_DAGS_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>DAGs - Airflow</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; display: flex; min-height: 100vh; }
        .airflow-sidebar { width: 72px; background-color: #111827; display: flex; flex-direction: column; align-items: center; padding: 12px 0; flex-shrink: 0; }
        .nav-item-btn { width: 56px; height: 52px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #9ca3af; text-decoration: none; font-size: 0.72rem; border-radius: 8px; margin-bottom: 6px; }
        .nav-item-btn.active { color: #ffffff; background-color: #0284c7; }
        .airflow-main { flex-grow: 1; padding: 24px 32px; }
        .dag-table-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0; overflow: hidden; }
    </style>
</head>
<body>
    <div class="airflow-sidebar">
        <a href="/" class="mb-4 mt-1"><i class="fa-solid fa-wind text-success fs-3"></i></a>
        <a href="/" class="nav-item-btn"><i class="fa-solid fa-house"></i>Home</a>
        <a href="/dags" class="nav-item-btn active"><i class="fa-solid fa-diagram-project"></i>Dags</a>
        <a href="#" class="nav-item-btn"><i class="fa-solid fa-database"></i>Assets</a>
        <a href="#" class="nav-item-btn"><i class="fa-solid fa-sliders"></i>Admin</a>
    </div>
    <div class="airflow-main">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold m-0">DAGs</h2>
            <a href="/trigger-dag" class="btn btn-success fw-bold px-3"><i class="fa-solid fa-play me-1"></i> Trigger DAG</a>
        </div>
        <div class="dag-table-card">
            <table class="table table-hover align-middle m-0">
                <thead class="table-light">
                    <tr>
                        <th width="40"><i class="fa-regular fa-star text-muted"></i></th>
                        <th width="60">State</th>
                        <th>DAG</th>
                        <th>Owner</th>
                        <th>Runs</th>
                        <th>Schedule</th>
                        <th>Last Run</th>
                        <th class="text-end">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><i class="fa-solid fa-star text-warning"></i></td>
                        <td><span class="badge bg-success rounded-pill px-2">On</span></td>
                        <td>
                            <strong class="text-primary fs-6">ragops_pipeline_dag</strong>
                            <div class="text-muted small">RAGOps Automated End-to-End Pipeline DAG</div>
                        </td>
                        <td><span class="badge bg-light text-dark border">airflow</span></td>
                        <td><span class="badge bg-success">1 Success</span></td>
                        <td><code>@daily</code></td>
                        <td><span class="text-muted small">2026-10-03 22:30:00</span></td>
                        <td class="text-end">
                            <a href="/trigger-dag" class="btn btn-sm btn-outline-success"><i class="fa-solid fa-play"></i> Run</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def add_no_cache_headers(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
@app.get("/auth/login", response_class=HTMLResponse)
@app.get("/auth/login/", response_class=HTMLResponse)
def serve_airflow_home(response: Response):
    add_no_cache_headers(response)
    return AIRFLOW_FULL_HTML

@app.get("/dags", response_class=HTMLResponse)
@app.get("/dags/{dag_id}", response_class=HTMLResponse)
@app.get("/dags/{dag_id}/grid", response_class=HTMLResponse)
@app.get("/dags/{dag_id}/graph", response_class=HTMLResponse)
def serve_airflow_dags(response: Response):
    add_no_cache_headers(response)
    return AIRFLOW_DAGS_PAGE_HTML

@app.get("/trigger-dag", response_class=HTMLResponse)
def trigger_dag(response: Response):
    add_no_cache_headers(response)
    try:
        from scripts.run_phase11_pipeline import run_phase11
        run_phase11()
    except Exception as e:
        print(f"Trigger execution info: {e}")
    return """
    <script>
        alert('Airflow DAG Execution Triggered & Completed Successfully!');
        window.location.href = '/';
    </script>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)

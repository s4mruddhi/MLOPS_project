"""
Assignment No. 4 DAG Execution Runner.
Runs extract -> validate -> process -> report -> notify sequentially.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dags.data_pipeline_dag import extract, validate, process, report, notify

def run_assignment4_pipeline():
    print("=" * 80)
    print("ASSIGNMENT NO. 4: APACHE AIRFLOW WORKFLOW EXECUTION RUNNER")
    print("DAG ID: data_pipeline_dag")
    print("=" * 80)

    tasks = [
        ("Task 1: extract", extract),
        ("Task 2: validate", validate),
        ("Task 3: process", process),
        ("Task 4: report", report),
        ("Task 5: notify", notify)
    ]

    start_time = time.time()
    results = []

    for name, func in tasks:
        t0 = time.time()
        print(f"\n---> Executing {name}...")
        try:
            res = func()
            duration = time.time() - t0
            results.append((name, "SUCCESS", duration))
        except Exception as e:
            duration = time.time() - t0
            results.append((name, f"FAILED: {e}", duration))
            print(f"[X] {name} FAILED: {e}")
            raise e

    total_time = time.time() - start_time

    print("\n" + "=" * 80)
    print("ASSIGNMENT NO. 4 DAG EXECUTION SUMMARY")
    print("=" * 80)
    for name, status, duration in results:
        print(f"{name:<25} | {status:<12} | {duration:.4f}s")
    print("=" * 80)
    print(f"Total Workflow Execution Time: {total_time:.4f} seconds")
    print("=" * 80)

if __name__ == "__main__":
    run_assignment4_pipeline()

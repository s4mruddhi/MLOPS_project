"""
Mock Tool Execution Engine for Agentic RAG.
"""

import time
from typing import Dict, Any, Tuple
from benchmark.schema import ToolCallTrace


class MockToolRegistry:
    """Executes agent tool calls and logs execution traces."""

    @staticmethod
    def get_cluster_status(cluster_id: str) -> Dict[str, Any]:
        if cluster_id == "db-us-east-1":
            return {
                "cluster_id": "db-us-east-1",
                "status": "HEALTHY",
                "primary_node": "db-us-east-1-primary",
                "cpu_utilization_pct": 42.0,
                "active_alerts": 0,
            }
        return {"cluster_id": cluster_id, "status": "NOT_FOUND", "error": "Unknown cluster ID"}

    @staticmethod
    def query_audit_logs(user_id: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "total_records": limit,
            "logs": [{"event": "LOGIN", "status": "SUCCESS", "timestamp": "2026-10-02T12:00:00Z"}],
        }

    def execute_tool(self, tool_name: str, input_args: Dict[str, Any]) -> ToolCallTrace:
        start_time = time.perf_counter()

        try:
            if tool_name == "get_cluster_status":
                res = self.get_cluster_status(**input_args)
                status = "success" if res.get("status") != "NOT_FOUND" else "error"
                err_msg = None if status == "success" else res.get("error")
            elif tool_name == "query_audit_logs":
                res = self.query_audit_logs(**input_args)
                status = "success"
                err_msg = None
            else:
                res = None
                status = "error"
                err_msg = f"Unknown tool name: '{tool_name}'"
        except Exception as e:
            res = None
            status = "error"
            err_msg = str(e)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return ToolCallTrace(
            tool_name=tool_name,
            input_args=input_args,
            output=res,
            status=status,
            execution_time_ms=elapsed_ms,
            error_message=err_msg,
        )

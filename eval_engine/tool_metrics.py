"""
Tool & Agentic Execution Metrics Evaluator.
Audits tool selection accuracy, argument validity, and execution reliability.
"""

from typing import List, Dict, Any
from benchmark.schema import ToolCallTrace, ToolMetrics


class ToolExecutionEvaluator:
    """Evaluates agentic tool calling traces against benchmark expectations."""

    @staticmethod
    def compute_metrics(
        executed_tools: List[ToolCallTrace], expected_tools: List[Dict[str, Any]]
    ) -> ToolMetrics:
        if not expected_tools:
            # If no tools were expected, 1.0 if none called, 1.0 if successful extra tools
            success_count = sum(1 for t in executed_tools if t.status == "success")
            total = len(executed_tools)
            tool_success_rate = success_count / total if total > 0 else 1.0
            return ToolMetrics(
                tool_selection_accuracy=1.0,
                param_match_rate=1.0,
                tool_success_rate=tool_success_rate,
            )

        expected_names = [e["tool_name"] for e in expected_tools]
        executed_names = [t.tool_name for t in executed_tools]

        # 1. Selection Accuracy (Overlap between expected tools and executed tools)
        matched_tools = set(expected_names).intersection(set(executed_names))
        selection_accuracy = len(matched_tools) / len(set(expected_names))

        # 2. Parameter Match Rate
        param_matches = 0
        for exp in expected_tools:
            exp_name = exp["tool_name"]
            exp_args = exp["input_args"]

            for trace in executed_tools:
                if trace.tool_name == exp_name:
                    # Compare args
                    if trace.input_args == exp_args:
                        param_matches += 1
                        break

        param_match_rate = param_matches / len(expected_tools)

        # 3. Execution Success Rate
        success_count = sum(1 for t in executed_tools if t.status == "success")
        success_rate = success_count / len(executed_tools) if executed_tools else 0.0

        return ToolMetrics(
            tool_selection_accuracy=round(selection_accuracy, 4),
            param_match_rate=round(param_match_rate, 4),
            tool_success_rate=round(success_rate, 4),
        )

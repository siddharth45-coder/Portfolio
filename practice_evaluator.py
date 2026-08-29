"""Evaluate public and hidden practice tests without exposing hidden outputs."""

from practice_execution import execute_python_solution


def evaluate_solution(problem: dict, source: str, include_hidden: bool) -> dict:
    """Evaluate a solution and return safe, display-ready test information."""
    cases = problem["public_tests"] + (problem["hidden_tests"] if include_hidden else [])
    execution = execute_python_solution(source, problem["function_name"], cases)
    if execution["status"] != "ok":
        return {**execution, "passed": 0, "total": len(cases), "is_solved": False, "public_results": []}
    public_count = len(problem["public_tests"])
    passed_flags = [result["actual"] == result["expected"] for result in execution["results"]]
    public_results = [
        {"passed": passed_flags[index], "actual": result["actual"], "expected": result["expected"]}
        for index, result in enumerate(execution["results"][:public_count])
    ]
    return {
        **execution, "passed": sum(passed_flags), "total": len(cases),
        "is_solved": all(passed_flags), "public_results": public_results,
    }

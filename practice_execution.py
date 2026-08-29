"""Best-effort local subprocess execution for CodeStreak Python solutions.

This is a development-only safety boundary, not a production-grade sandbox.
Run untrusted code in a dedicated container or sandbox service before public use.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


EXECUTION_TIMEOUT_SECONDS = 3
MAX_OUTPUT_CHARS = 10_000


def execute_python_solution(source: str, function_name: str, cases: list[tuple]) -> dict:
    """Run one Python function against cases in a child process with a timeout."""
    harness = (
        source
        + "\n\nimport json\n"
        + f"_cases = {cases!r}\n_results = []\n"
        + f"for _case in _cases:\n    _args, _expected = _case[:-1], _case[-1]\n    _results.append({{'actual': {function_name}(*_args), 'expected': _expected}})\n"
        + "print(json.dumps(_results))\n"
    )
    with tempfile.TemporaryDirectory(prefix="codestreak-practice-") as directory:
        script = Path(directory) / "solution.py"
        script.write_text(harness, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-I", str(script)], cwd=directory, text=True,
                capture_output=True, timeout=EXECUTION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "stdout": "", "stderr": "Execution timed out.", "results": []}

    stdout, stderr = result.stdout[:MAX_OUTPUT_CHARS], result.stderr[:MAX_OUTPUT_CHARS]
    if result.returncode != 0:
        status = "syntax_error" if "SyntaxError" in stderr else "runtime_error"
        return {"status": status, "stdout": stdout, "stderr": stderr, "results": []}
    try:
        results = json.loads(stdout)
    except json.JSONDecodeError:
        return {"status": "runtime_error", "stdout": stdout, "stderr": "Solution returned unreadable output.", "results": []}
    return {"status": "ok", "stdout": stdout, "stderr": stderr, "results": results}

import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Tuple

from langchain_core.tools import tool


def get_test_dir() -> Path:
    """Get or create a directory for test files."""
    test_dir = Path.cwd() / "test_files"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@tool
def run_tests_with_results(
    test_code: Annotated[str, "The PyTest code written to test the source code."],
    source_code: Annotated[
        str, "The Python source code for which the tests are written."
    ],
) -> Annotated[
    Tuple[str, str, str],
    "Tuple of: the PyTest test output including stdout and stderr, the PyTest code including the unit tests, the Python source code that was tested.",
]:
    """This function runs pytest on the given Python test code string and
    captures the test output."""
    test_dir = get_test_dir()

    source_path = test_dir / "source.py"
    with open(source_path, "w") as f:
        f.write(source_code)

    test_path = test_dir / "test_source.py"
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        # Use the current Python executable and its environment
        python_executable = sys.executable
        env = os.environ.copy()
        # Add the test directory to Python path
        python_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{test_dir}{os.pathsep}{python_path}"

        result = subprocess.run(
            [python_executable, "-m", "pytest", "-v", "--tb=long", str(test_path)],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        output = "Test output:\n```\n" + result.stdout
        if result.stderr:
            output += result.stderr
        output += "\n```"

        return output, test_code, source_code

    except PermissionError as e:
        raise PermissionError(f"Permission denied accessing test file: {str(e)}")
    except subprocess.SubprocessError as e:
        raise subprocess.SubprocessError(f"Failed to execute pytest: {str(e)}")
    finally:
        # Clean up the files
        try:
            source_path.unlink(missing_ok=True)
            test_path.unlink(missing_ok=True)
        except Exception:
            pass


@tool
def did_tests_pass(
    test_code: Annotated[str, "The PyTest code written to test the source code."],
    source_code: Annotated[
        str, "The Python source code for which the tests are written."
    ],
) -> Annotated[
    Tuple[bool, str, str],
    "Tuple of: a boolean if all test passed, the PyTest code including the unit tests, the Python source to that was tested.",
]:
    """Runs pytest on provided Python code and returns test results and
    output."""
    test_dir = get_test_dir()

    source_path = test_dir / "source.py"
    with open(source_path, "w") as f:
        f.write(source_code)

    test_path = test_dir / "test_source.py"
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        # Use the current Python executable and its environment
        python_executable = sys.executable
        env = os.environ.copy()
        # Add the test directory to Python path
        python_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{test_dir}{os.pathsep}{python_path}"

        result = subprocess.run(
            [python_executable, "-m", "pytest", str(test_path), "--capture=sys"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            env=env,
        )
        return result.returncode == 0, test_code, source_code

    except FileNotFoundError:
        raise FileNotFoundError(
            "pytest not found. Please install pytest: pip install pytest"
        )
    finally:
        # Clean up the files
        try:
            source_path.unlink(missing_ok=True)
            test_path.unlink(missing_ok=True)
        except Exception:
            pass


validation_tools = [run_tests_with_results, did_tests_pass]

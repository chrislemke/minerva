import ast
import os
from pathlib import Path
from typing import Dict

from code_analyzer import CodeAnalyzer


def _should_skip_file(file_path: Path) -> bool:
    """Determine if a file should be skipped for test generation.

    Args:
        file_path (Path): Path to the Python file to analyze

    Returns:
        bool: True if the file should be skipped, False otherwise
    """
    skip_patterns = {
        "patterns": [
            "constant",
            "const",
            "value",
            "setting",
            "config",
            "version",
            "type",
            "enum",
            "exception",
            "error",
            "__init__",
            "interface",
            "stub",
            "helper",
            "util",
            "mock",
            "fake",
        ],
        "content_markers": [
            "typing.",
            "@dataclass",
            "enum.",
            "logging.",
            "@abstractmethod",
            "@interface",
            "Protocol",
            "TypeVar",
            "@overload",
        ],
        "external_deps": {
            "requests",
            "aiohttp",
            "httpx",
            "sqlalchemy",
            "django",
            "flask",
            "fastapi",
            "boto3",
            "azure",
            "google.cloud",
            "pymongo",
            "redis",
            "celery",
            "kafka",
            "rabbitmq",
            "pika",
        },
    }

    if any(pattern in file_path.stem.lower() for pattern in skip_patterns["patterns"]):
        return True

    try:
        content = file_path.read_text(encoding="utf-8")

        if len(content.strip()) < 50:
            return True

        tree = ast.parse(content)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)

        if not analyzer.has_testable_code:
            return True

        if analyzer.import_names & skip_patterns["external_deps"]:  # type: ignore
            return True

        if analyzer.has_api_calls or analyzer.has_db_operations:
            return True

        content_lower = content.lower()
        marker_matches = sum(
            1 for marker in skip_patterns["content_markers"] if marker in content_lower
        )

        if marker_matches > 2 or analyzer.decorator_count > 5:
            return True

        return False

    except Exception as e:
        print(f"Error analyzing file {file_path}: {str(e)}")
        return False


def read_python_files(folder_path: str) -> Dict[str, str]:
    """Read all Python files in the specified folder and return their contents
    as a dictionary.

    Args:
        folder_path (str): Path to the folder containing Python files

    Returns:
        Dict[str, str]: Dictionary where keys are file names (without .py) and values are file contents
    """

    folder = Path(folder_path)
    result = {}

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"The path {folder_path} does not exist or is not a directory")

    for python_file in folder.glob("*.py"):
        if not _should_skip_file(python_file):
            try:
                content = python_file.read_text(encoding="utf-8")
                result[python_file.stem] = content
            except Exception as e:
                print(f"Error reading file {python_file}: {str(e)}")
                continue

    return result


def write_test_python_module(content: str, file_path: str):
    """Writes the given string content to a Python file at the specified
    location.

    Parameters:
    - content (str): The string to write to the file.
    - file_path (str): The path where the Python file will be stored.

    Raises:
    - ValueError: If the file path does not end with '.py'.
    """
    if not file_path.endswith(".py"):
        raise ValueError("The file path must end with '.py'")

    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as file:
        file.write(content)


def get_file_path_from_user(text: str) -> str:
    while True:
        test_path = input(text).strip()

        path = Path(test_path).resolve()

        if not path.exists():
            print(f"Error: Path '{path}' does not exist.")
            continue

        if not path.is_dir():
            print(f"Error: '{path}' is not a directory.")
            continue
        return path.as_posix()

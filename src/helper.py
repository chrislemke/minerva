import ast
import os
from pathlib import Path
from typing import List


def clean_python_code(text: str) -> str:
    """Cleans a string containing Python code mixed with natural language,
    preserving only valid Python code, blank lines, comments, and docstrings.

    Args:
        text (str): Input text containing Python code and natural language

    Returns:
        str: Cleaned text with natural language removed
    """

    def try_parse_line(line: str) -> bool:
        """Check if a single line could be part of valid Python code."""
        stripped = line.strip()
        if not stripped:
            return True

        if any(
            [
                stripped.startswith("#"),
                stripped.startswith(('"""', "'''")),
                stripped.startswith(("import ", "from ")),
                stripped.startswith(("def ", "class ")),
                stripped.startswith("@"),
                stripped.startswith(
                    ("if ", "elif ", "else:", "try:", "except", "finally:")
                ),
                stripped.startswith(("while ", "for ")),
                stripped.startswith(("return ", "yield ", "raise ")),
                stripped in ("pass", "break", "continue"),
                stripped.startswith("print("),
                "=" in stripped,
            ]
        ):
            return True

        if line.startswith((" ", "\t")):
            return True

        try:
            ast.parse(stripped, mode="eval")
            return True
        except:
            pass

        return False

    lines = text.split("\n")
    result_lines = []
    in_multiline_string = False

    for line in lines:
        stripped = line.strip()
        if stripped.count('"""') % 2 == 1 or stripped.count("'''") % 2 == 1:
            in_multiline_string = not in_multiline_string

        if not stripped or in_multiline_string or try_parse_line(line):
            result_lines.append(line)

    result = "\n".join(result_lines)

    try:
        ast.parse(result)
        return result
    except:
        final_lines = []
        current_block: List[str] = []

        for line in result.split("\n"):
            if not line.strip():
                if current_block:
                    try:
                        ast.parse("\n".join(current_block))
                        final_lines.extend(current_block)
                        final_lines.append(line)
                    except:
                        pass
                    current_block = []
                else:
                    final_lines.append(line)
            else:
                current_block.append(line)

        if current_block:
            try:
                ast.parse("\n".join(current_block))
                final_lines.extend(current_block)
            except:
                pass

        return "\n".join(final_lines)


def get_relative_source_path(source_path: str, test_path: str) -> str:
    """Get the relative path from the test directory to the source directory.

    Args:
        source_path (str): Path to directory containing source Python files
        test_path (str): Path to directory containing test files

    Returns:
        str: The relative path that was added to sys.path
    """
    source_path_obj = Path(source_path).resolve()
    test_path_obj = Path(test_path).resolve()

    # Find the common parent directory
    common_parent = None
    source_parents = list(source_path_obj.parents)
    test_parents = list(test_path_obj.parents)

    for sp in source_parents:
        if sp in test_parents:
            common_parent = sp
            break

    if not common_parent:
        raise ValueError(
            "No common parent directory found between source and test paths"
        )

    return os.path.relpath(str(source_path_obj), str(test_path_obj))

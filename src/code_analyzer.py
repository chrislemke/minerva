import ast
from typing import Set


class CodeAnalyzer(ast.NodeVisitor):
    """Analyzes Python code to detect patterns that suggest a file might not
    need unit tests."""

    def __init__(self) -> None:
        self.has_api_calls: bool = False
        self.has_external_deps: bool = False
        self.has_db_operations: bool = False
        self.has_file_operations: bool = False
        self.decorator_count: int = 0
        self.import_names: Set[str] = set()
        self.has_testable_code: bool = False

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            if any(
                name in str(node.func.attr).lower()
                for name in ["get", "post", "put", "delete", "patch", "request"]
            ):
                self.has_api_calls = True

        if isinstance(node.func, ast.Name):
            db_patterns = {
                "execute",
                "commit",
                "rollback",
                "query",
                "insert",
                "update",
                "delete",
            }
            if node.func.id in db_patterns:
                self.has_db_operations = True

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            self.import_names.add(name.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.import_names.add(node.module.split(".")[0])
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not any(
            d.id == "abstractmethod"
            for d in node.decorator_list
            if isinstance(d, ast.Name)
        ):
            self.has_testable_code = True
        self.decorator_count += len(node.decorator_list)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not any(
            d.id == "abstractmethod"
            for d in node.decorator_list
            if isinstance(d, ast.Name)
        ):
            self.has_testable_code = True
        self.decorator_count += len(node.decorator_list)
        self.generic_visit(node)

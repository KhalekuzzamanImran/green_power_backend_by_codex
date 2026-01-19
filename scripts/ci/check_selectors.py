#!/usr/bin/env python
import ast
import sys
from pathlib import Path

SELECTORS_ROOT = Path(__file__).resolve().parents[2] / "apps"

WRITE_PATTERNS = [
    ".save(",
    ".delete(",
    ".create(",
    ".update(",
    ".bulk_create(",
    ".bulk_update(",
    ".get_or_create(",
    ".update_or_create(",
]


class SelectorChecker(ast.NodeVisitor):
    def __init__(self, path: Path):
        self.path = path
        self.errors: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.returns is None:
            self.errors.append(f"{self.path}:{node.lineno} selector missing return annotation")
        else:
            annotation = ast.unparse(node.returns)
            if "User" in annotation or "Model" in annotation or "QuerySet" in annotation:
                self.errors.append(
                    f"{self.path}:{node.lineno} selector returns ORM type: {annotation}"
                )
        self.generic_visit(node)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for pattern in WRITE_PATTERNS:
        if pattern in text:
            errors.append(f"{path}: selector contains ORM write API: {pattern}")
            break
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        errors.append(f"{path}: syntax error: {exc}")
        return errors
    checker = SelectorChecker(path)
    checker.visit(tree)
    errors.extend(checker.errors)
    return errors


def main() -> int:
    errors: list[str] = []
    selector_files = SELECTORS_ROOT.glob("*/selectors/*.py")
    for path in selector_files:
        if path.name == "__init__.py":
            continue
        errors.extend(check_file(path))
    if errors:
        print("Selector contract violations:")
        for err in errors:
            print(f"- {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

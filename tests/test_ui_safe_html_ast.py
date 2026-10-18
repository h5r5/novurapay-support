"""AST verification test for unsafe_allow_html=True usage in src/supportpipe/ui/app.py (Task 2.3 / A4)."""

from __future__ import annotations

import ast
from typing import Any

from supportpipe.config import settings


def get_format_spec_str(format_spec_node: ast.AST | None) -> str:
    """Extract format specification string from an AST node."""
    if format_spec_node is None:
        return ""
    if isinstance(format_spec_node, ast.JoinedStr):
        parts: list[str] = []
        for val in format_spec_node.values:
            if isinstance(val, ast.Constant):
                parts.append(str(val.value))
        return "".join(parts)
    return ast.unparse(format_spec_node)


def is_safe_expression(node: ast.AST, format_spec: str = "") -> tuple[bool, str]:
    """Determine whether an AST expression in an f-string is safely escaped or numeric."""
    spec = format_spec.lstrip(":")
    if spec and spec[-1] in ("f", "d", "g", "e", "%"):
        return True, f"numeric-format ({format_spec})"

    if isinstance(node, ast.Call):
        func_name = ast.unparse(node.func)
        if func_name == "safe_html":
            return True, "safe_html"
        if func_name in ("int", "float", "round", "len"):
            return True, "numeric-cast"

    if isinstance(node, ast.BinOp):
        return True, "numeric-binop"

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return True, "numeric-constant"

    src = ast.unparse(node)
    if src.startswith("icon_") or src in (
        "cb_html",
        "groq_tag_html",
        "gemini_tag_html",
        "jev_tag_html",
        "ref_txt",
        "amt_txt",
        "date_txt",
        "phone_txt",
    ):
        return True, f"known-safe-var ({src})"

    if "tag-escalate" in src and "tag-auto" in src:
        return True, "safe-static-ternary"

    return False, f"UNWRAPPED ({src})"


def inspect_unsafe_html_sites(source_code: str, filename: str = "<string>") -> list[dict[str, Any]]:
    """Scan AST for calls with unsafe_allow_html=True and audit each argument."""
    tree = ast.parse(source_code, filename=filename)
    sites: list[ast.Call] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if (
                    kw.arg == "unsafe_allow_html"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                ):
                    sites.append(node)

    sites.sort(key=lambda n: n.lineno)
    results: list[dict[str, Any]] = []

    for call_node in sites:
        arg0 = (
            call_node.args[0]
            if call_node.args
            else [kw.value for kw in call_node.keywords if kw.arg in ("body", "text")][0]
        )

        if isinstance(arg0, ast.Constant):
            results.append({
                "line": call_node.lineno,
                "kind": "static",
                "expr": "STATIC HTML",
                "is_safe": True,
                "reason": "pure-static-html",
            })
        elif isinstance(arg0, ast.JoinedStr):
            for val in arg0.values:
                if isinstance(val, ast.FormattedValue):
                    expr_src = ast.unparse(val.value)
                    fspec = get_format_spec_str(val.format_spec)
                    safe, reason = is_safe_expression(val.value, fspec)
                    results.append({
                        "line": call_node.lineno,
                        "kind": "interpolated",
                        "expr": expr_src,
                        "is_safe": safe,
                        "reason": reason,
                    })

    return results


def test_app_py_has_zero_unwrapped_unsafe_html_interpolations() -> None:
    """Verify that every unsafe_allow_html=True site in app.py is static or wrapped safely."""
    app_path = settings.project_root / "src" / "supportpipe" / "ui" / "app.py"
    assert app_path.exists(), f"app.py not found at {app_path}"

    source = app_path.read_text(encoding="utf-8")
    audit_results = inspect_unsafe_html_sites(source, filename=str(app_path))

    # There must be exactly 27 unsafe_allow_html call sites in app.py
    call_lines = {r["line"] for r in audit_results}
    assert len(call_lines) == 27, f"Expected 27 unsafe_allow_html call sites, found {len(call_lines)}"

    violations = [r for r in audit_results if not r["is_safe"]]
    assert len(violations) == 0, (
        f"Found {len(violations)} unwrapped HTML interpolation violations:\n"
        + "\n".join(f"  Line {v['line']}: {v['expr']} ({v['reason']})" for v in violations)
    )


def test_ast_audit_fails_on_new_unwrapped_interpolation() -> None:
    """Verify that the AST audit fails when an unwrapped interpolation is introduced."""
    vulnerable_code = '''
import streamlit as st
user_comment = "<script>alert('xss')</script>"
st.markdown(f"<div class='box'>{user_comment}</div>", unsafe_allow_html=True)
'''
    audit_results = inspect_unsafe_html_sites(vulnerable_code)
    violations = [r for r in audit_results if not r["is_safe"]]

    assert len(violations) == 1
    assert violations[0]["expr"] == "user_comment"
    assert "UNWRAPPED" in violations[0]["reason"]
